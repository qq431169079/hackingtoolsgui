from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.urls import reverse, resolve
from django.views.decorators.csrf import csrf_exempt
from .library import hackingtools as ht
from .library.hackingtools.core import Utils, Logger, Config
from importlib import reload
import os
import json
from requests import Response
from colorama import Fore

from .views_modules import *

# Create your views here.

config = Config.getConfig(parentKey='django', key='views')
global ht_data
ht_data = {}

def load_data():
    global ht_data
    modules_and_params = ht.getModulesJSON()
    modules_forms = ht.__getModulesDjangoForms__()
    modules_forms_modal = ht.__getModulesDjangoFormsModal__()
    modules_config = ht.getModulesConfig()
    modules_config_treeview = ht.__getModulesConfig_treeView__()
    modules_functions_modals = ht.getModulesModalTests()
    modules_functions_calls_console_string = ht.getModulesFunctionsCalls()
    modules_all = {}
    categories = []
    for mod in modules_and_params:
        if not mod.split('.')[1] in categories:
            categories.append(mod.split('.')[1])
        modules_all[mod.split('.')[2]] = modules_and_params[mod]
    modules_names = ht.getModulesNames()
    pool_list = ht.getPoolNodes()
    my_node_id_pool = ht.MY_NODE_ID
    status_pool = ht.WANT_TO_BE_IN_POOL
    ht_data =  { 
        'modules':modules_names, 
        'categories':categories, 
        'modules_all':modules_all,
        'modules_forms':modules_forms, 
        'modules_forms_modal':modules_forms_modal, 
        'modules_config':modules_config, 
        'console_command':modules_functions_calls_console_string, 
        'modules_config_treeview':modules_config_treeview, 
        'modules_functions_modals':modules_functions_modals, 
        'pool_list':pool_list,
        'my_node_id_pool':my_node_id_pool,
        'status_pool':status_pool}

def renderMainPanel(request, popup_text=''):
    global ht_data
    if not ht_data:
        load_data()
    if popup_text != '':
        ht_data['popup_text'] = popup_text
    return render(request, 'core/index.html', dict(ht_data))

def home(request, popup_text=''):
    global ht_data
    load_data()
    if popup_text != '':
        ht_data['popup_text'] = popup_text
    return renderMainPanel(request=request)

def documentation(request, module_name=''):
    this_conf = config['documentation']
    if module_name:
        for mod in ht.modules_loaded:
            if module_name == mod.split('.')[-1]:
                doc_mod = '{documents_dir}/{c}/{b}/{a}.html'.format(documents_dir=this_conf['documents_dir'], c=mod.split('.')[-3], b=module_name.split('ht_')[1], a=module_name)
                categories = []
                for mod in ht.getModulesJSON():
                    if not mod.split('.')[1] in categories:
                        categories.append(mod.split('.')[1])
                modules_names = ht.getModulesNames()
                return render(request, this_conf['html_template'], { 'doc_mod' : doc_mod, 'categories' : categories, 'modules' : modules_names })
        return renderMainPanel(request=request, popup_text=this_conf['bad_module'])
    else:
        return renderMainPanel(request=request, popup_text=this_conf['no_module_selected'])

def sendPool(request, functionName):
    # ! changes here affect all nodes on the network, so should be careful with this
    # ! It loop inside all nodes's known nodes
    response, creator, = ht.send(request, functionName)
    if response:
        if creator == ht.MY_NODE_ID:
            if 'nodes_pool' in response:
                for n in response['nodes_pool']:
                    ht.addNodeToPool(n)
            return response, False
        return response, True
    return None, None

def switchPool(request):
    ht.switchPool()
    data = {
        'status' : ht.WANT_TO_BE_IN_POOL
    }
    return JsonResponse(data)

def createModule(request):
    mod_name = request.POST.get('module_name').replace(" ", "_").lower()
    mod_cat = request.POST.get('category_name')
    created = ht.createModule(mod_name, mod_cat)
    if created:
        modules_and_params = ht.getModulesJSON()
    return renderMainPanel(request=request)

def configModule(request):
    mod_name = request.POST.get('module_name').replace(" ", "_").lower()
    mod_conf = ht.getModuleConfig(mod_name)
    reload(ht)
    return renderMainPanel(request=request)

def createCategory(request):
    mod_cat = request.POST.get('category_name').replace(" ", "_").lower()
    ht.createCategory(mod_cat)
    return renderMainPanel(request=request)

def createScript(request):
    return renderMainPanel(request=request)

def config_look_for_changes(request):
    ht.Config.__look_for_changes__()
    load_data()
    return renderMainPanel(request=request)

def saveFileOutput(myfile, module_name, category):
    location = os.path.join("core", "library", "hackingtools", "modules", category, module_name.split('ht_')[0], "output")
    fs = FileSystemStorage(location=location)
    filename = fs.save(myfile.name, myfile)
    Logger.printMessage(message='saveFileOutput', description='Saving to {fi}'.format(fi=os.path.join(location,myfile.name)))
    return (filename, location, os.path.join(location, filename))

@csrf_exempt
def add_pool_node(request):
    this_conf = config['add_pool_node']
    try:
        if request.POST:
            pool_node = request.POST.get('pool_ip')
        ht.addNodeToPool(pool_node)
        if request.POST.get('is_async', False):
            data = {
                'data' : ht.getPoolNodes()
            }
            return JsonResponse(data)
        return renderMainPanel(request=request, popup_text='\n'.join(ht.getPoolNodes()))
    except:
        return renderMainPanel(request=request, popup_text=this_conf['error'])
    return renderMainPanel(request=request, popup_text='\n'.join(ht.getPoolNodes()))

def getDictionaryAlphabet(numeric=True, lower=False, upper=False, simbols14=False, simbolsAll=False):
    used_alphabet = 'numeric'
    if numeric and not lower and not upper and not simbols14 and not simbolsAll:
        used_alphabet = 'numeric'
    if not numeric and lower and not upper and not simbols14 and not simbolsAll:
        used_alphabet = 'lalpha'
    if not numeric and not lower and upper and not simbols14 and not simbolsAll:
        used_alphabet = 'ualpha'
    if not numeric and lower and upper and not simbols14 and not simbolsAll:
        used_alphabet = 'mixalpha'
    if not numeric and not lower and not upper and simbols14 and not simbolsAll:
        used_alphabet = 'symbols14'
    if not numeric and not lower and not upper and not simbols14 and simbolsAll:
        used_alphabet = 'symbols-all'

    if not numeric and lower and not upper and simbols14 and not simbolsAll:
        used_alphabet = 'lalpha-symbol14'
    if not numeric and lower and not upper and not simbols14 and simbolsAll:
        used_alphabet = 'lalpha-all'
    if numeric and lower and not upper and not simbols14 and not simbolsAll:
        used_alphabet = 'lalpha-numeric'
    if numeric and lower and not upper and simbols14 and not simbolsAll:
        used_alphabet = 'lalpha-numeric-symbol14'
    if numeric and lower and not upper and not simbols14 and simbolsAll:
        used_alphabet = 'lalpha-numeric-all'

    if not numeric and not lower and upper and simbols14 and not simbolsAll:
        used_alphabet = 'ualpha-symbol14'
    if not numeric and not lower and upper and not simbols14 and simbolsAll:
        used_alphabet = 'ualpha-all'
    if numeric and not lower and upper and not simbols14 and not simbolsAll:
        used_alphabet = 'ualpha-numeric'
    if numeric and not lower and upper and simbols14 and not simbolsAll:
        used_alphabet = 'ualpha-numeric-symbol14'
    if numeric and not lower and upper and not simbols14 and simbolsAll:
        used_alphabet = 'ualpha-numeric-all'

    if not numeric and lower and upper and simbols14 and not simbolsAll:
        used_alphabet = 'mixalpha-symbol14'
    if not numeric and lower and upper and not simbols14 and simbolsAll:
        used_alphabet = 'mixalpha-all'
    if numeric and lower and upper and not simbols14 and not simbolsAll:
        used_alphabet = 'mixalpha-numeric'
    if numeric and lower and upper and simbols14 and not simbolsAll:
        used_alphabet = 'mixalpha-numeric-symbol14'
    if numeric and lower and upper and not simbols14 and simbolsAll:
        used_alphabet = 'mixalpha-numeric-all'

    return used_alphabet

