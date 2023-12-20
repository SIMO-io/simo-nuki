from simo.core.controllers import Lock
from .gateways import NukiGatewayHandler
from .forms import NukiLock
from .models import NukiDevice


class NuckiLock(Lock):
    gateway_class = NukiGatewayHandler
    config_form = NukiLock

    def _send_to_device(self, value):
        conf = self.component.config
        lock = NukiDevice.objects.get(id=conf['nuki_device'])
        if value:
            lock.lock()
        else:
            lock.unlock()
