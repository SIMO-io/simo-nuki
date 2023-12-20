import time
import datetime
from django.utils import timezone
from simo.core.gateways import BaseGatewayHandler
from simo.core.forms import BaseGatewayForm

from .models import NukiBridge
from .tasks import check_bridge_devices


class NukiGatewayHandler(BaseGatewayHandler):
    name = "Nuki"
    uid = 'NukiDevices'
    config_form = BaseGatewayForm

    def run(self, exit):
        while not exit.is_set():
            time.sleep(2)
            for bridge in NukiBridge.objects.filter(
                last_update__gt=timezone.now() - datetime.timedelta(hours=4)
            ):
                check_bridge_devices(bridge)
