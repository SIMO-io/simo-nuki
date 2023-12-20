import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, JsonResponse
from .models import NukiDevice


@csrf_exempt
def callback(request):
    if request.method != 'POST':
        raise Http404()

    data = json.loads(request.body)
    device = NukiDevice.objects.get(id=data['nukiId'])
    device.last_state_data = data
    device.last_state = data.get('stateName')
    device.save()

    HttpResponse("OK")
