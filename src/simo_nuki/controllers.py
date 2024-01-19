from simo.core.controllers import Lock
from .gateways import NukiGatewayHandler
from .forms import NukiLock
from .models import NukiDevice


class NuckiLock(Lock):
    gateway_class = NukiGatewayHandler
    config_form = NukiLock