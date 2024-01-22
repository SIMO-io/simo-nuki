import json
from django.utils import timezone
from simo.core.gateways import BaseObjectCommandsGatewayHandler
from simo.core.forms import BaseGatewayForm
from .models import NukiDevice



class NukiGatewayHandler(BaseObjectCommandsGatewayHandler):
    name = "Nuki"
    uid = 'NukiDevices'
    config_form = BaseGatewayForm

    def _on_mqtt_connect(self, mqtt_client, userdata, flags, rc):
        super()._on_mqtt_connect(mqtt_client, userdata, flags, rc)
        mqtt_client.subscribe('nuki/#')

    def _on_mqtt_message(self, client, userdata, msg):
        if msg.topic.startswith('nuki'):
            return self.handle_nuki_msg(msg)
        return super()._on_mqtt_message(client, userdata, msg)

    def perform_value_send(self, component, value):
        lock = NukiDevice.objects.get(id=component.config['nuki_device'])
        print(f"Perform {value} delivery to {lock}")
        if value == False:
            self.mqtt_client.publish(f'nuki/{lock.id}/lockAction', b'1')
        elif value == True:
            self.mqtt_client.publish(f'nuki/{lock.id}/lockAction', b'2')

    def handle_nuki_msg(self, msg):
        drop, device_id, topic = msg.topic.split('/')
        print("MESSAGE TOPIC: ", msg.topic)
        print("MESSAGE PAYLOAD: ", msg.payload)
        try:
            val = json.loads(msg.payload)
        except:
            val = msg.payload.decode()
        device, new = NukiDevice.objects.get_or_create(id=device_id)
        properties_map = {
            'deviceType': 'type',
            'name': 'name',
            'firmware': 'firmware_version',
        }
        if topic in properties_map:
            setattr(device, properties_map[topic], val)
            device.save()
            return

        if topic == 'state':
            states_map = {
                0: 'fault',
                1: 'locked',
                2: 'unlocking',
                3: 'unlocked',
                4: 'locking',
                5: 'unlocked',
                6: 'unlocked',
                7: 'unlocking',
                253: 'fault',
                254: 'fault',
                255: 'fault',
            }
            device.last_state = states_map.get(val, val)
            device.save()
            for component in device.components:
                component.controller._receive_from_device(device.last_state)
                component.save()
            return

        if topic == 'batteryChargeState':
            for component in device.components:
                component.battery_level = val
                component.save()
            return

        if topic == 'lockActionEvent':
            action_items = str(val).split(',')
            # register fingerprint on unlock events only
            if action_items[0] != '1':
                return
            from simo.users.models import Fingerprint
            for component in device.components:
                fingerprint, new = Fingerprint.objects.get_or_create(
                    value='nuki-' + ','.join(action_items[2:4]),
                    defaults={'user': component.zone.instance.learn_fingerprints}
                )
                component.change_init_date = timezone.now()
                component.change_init_fingerprint = fingerprint
                component.save()