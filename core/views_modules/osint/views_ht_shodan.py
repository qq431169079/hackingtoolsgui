from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
from requests import Response

from core import views
from core.views import ht, config, renderMainPanel, saveFileOutput, Logger

# Create your views here.

# ht_shodan

def getIPListfromServices(request):
    if request.POST.get('service_name'):
        service_name = request.POST.get('service_name')
        shodan_key = None
        if request.POST.get('shodanKeyString'):
            shodan_key = request.POST.get('shodanKeyString')
        shodan = ht.getModule('ht_shodan')
        response_shodan = shodan.getIPListfromServices(serviceName=service_name, shodanKeyString=shodan_key)
        resp_text = ','.join(response_shodan)
        if request.POST.get('is_async', False):
            data = {
                'data' : resp_text
            }
            return JsonResponse(data)
        return renderMainPanel(request=request, popup_text=resp_text)
    else:
        return renderMainPanel(request=request)

def search_host(request):
    if request.POST.get('service_ip'):
        service_ip = request.POST.get('service_ip')
        shodan = ht.getModule('ht_shodan')
        response_shodan = shodan.search_host(service_ip)
        if request.POST.get('is_async', False):
            data = {
                'data' : response_shodan
            }
            return JsonResponse(data)
        return renderMainPanel(request=request, popup_text=response_shodan)
    else:
        return renderMainPanel(request=request)

# End ht_shodan