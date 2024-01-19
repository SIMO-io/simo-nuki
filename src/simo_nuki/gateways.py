import json
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
                0: 'uncalibrated',
                1: 'locked',
                2: 'unlocking',
                3: 'unlocked',
                4: 'locking',
                5: 'unlatched',
                6: 'unlocked (lock ‘n’ go) ',
                7: 'unlatching',
                253: '-',
                254: 'motor blocked',
                255: 'undefined',
            }
            device.last_state = states_map.get(val, val)
            device.save()
            return

        if topic == 'batteryChargeState':
            for component in device.components:
                component.battery_level = val
                component.save()
            return







