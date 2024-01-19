import requests
import datetime
import urllib.parse
from django.urls import reverse
from django.utils import timezone
from celeryc import celery_app
from simo.core.utils.helpers import get_self_ip
from .models import NukiBridge, NukiDevice


@celery_app.task
def discover_nuki_bridges():
    resp = requests.get('https://api.nuki.io/discover/bridges')
    if resp.status_code != 200:
        return
    for item in resp.json().get('bridges', []):
        defaults = {
            'ip': item['ip'], 'port': item['port'],
            'last_update': timezone.now()
        }
        bridge, new = NukiBridge.objects.update_or_create(
            id=item['bridgeId'], defaults=defaults
        )
        if not bridge.token:
            get_bridge_token.delay(bridge.id)

        if bridge.token:
            check_bridge(bridge.id)
            check_bridge_devices(bridge.id)


@celery_app.task
def get_bridge_token(bridge_id):
    bridge = NukiBridge.objects.get(id=bridge_id)
    try:
        r = requests.get(f"http://{bridge.ip}:{bridge.port}/auth")
    except:
        pass
    else:
        if r.status_code == 200 and r.json().get('token'):
            bridge.token = r.json().get('token')
            bridge.save()


@celery_app.task
def check_bridge(bridge_id):
    bridge = NukiBridge.objects.get(id=bridge_id)
    resp = requests.get(
        f'http://{bridge.ip}:{bridge.port}/info?token={bridge.token}'
    )
    if resp.status_code != 200:
        return
    bridge.info = resp.json()
    bridge.save()

    our_callback_url = f'http://{get_self_ip()}' + reverse('nuki-callback')
    callback_ok = False
    resp = requests.get(
        f'http://{bridge.ip}:{bridge.port}/callback/list?token={bridge.token}'
    )
    if resp.status_code == 200:
        for item in resp.json().get('callbacks', []):
            if item['url'] == our_callback_url:
                callback_ok = True
                break
    if not callback_ok:
        url = urllib.parse.quote_plus(our_callback_url)
        requests.get(
            f'http://{bridge.ip}:{bridge.port}/callback/add'
            f'?token={bridge.token}&url={url}'
        )


@celery_app.task
def check_bridge_devices(bridge):
    if not isinstance(bridge, NukiBridge):
        bridge = NukiBridge.objects.get(id=bridge)
    resp = requests.get(
        f'http://{bridge.ip}:{bridge.port}/list?token={bridge.token}'
    )
    if resp.status_code != 200:
        return
    for item in resp.json():
        defaults = {
            'bridge': bridge,
            'type': item['deviceType'], 'name': item['name'],
            'firmware_version': item.get('firmwareVersion', ''),
            'last_state_data': item.get('lastKnownState'),
            'last_state': item.get('lastKnownState', {}).get('stateName', '')
        }
        defaults['last_update'] = timezone.now()
        NukiDevice.objects.update_or_create(
            id=item['nukiId'], defaults=defaults
        )
    bridge.info = resp.json()
    bridge.save()


@celery_app.task
def device_action(device_id, action):
    device = NukiDevice.objects.get(id=device_id)
    if device.bridge:
        requests.get(
            f'http://{device.bridge.ip}:{device.bridge.port}/'
            f'{action}?token={device.bridge.token}&nukiId={device.id}'
        )
    else:
        requests.get(
            f'http://{device.ip}:{device.port}/'
            f'{action}?token={device.token}&nukiId={device.id}'
        )


# @celery_app.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(60 * 60, discover_nuki_bridges.s()) # runs hourly



