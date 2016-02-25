import json

from django.shortcuts import render
from django.http import HttpResponse
from lobot.models import model_encode
from lobot.models import model_encode_verbose

###
### Request Handling
###

def get_request_var(request, name):
    var = None
    try:
        var = request.POST[name]
    except:
        try:
            var = request.GET[name]
        except:
            pass

    if var == '':
        var = None

    return var

###
### Responses
###

def error_dict(http_status_code=400):
    error_dict = _response_dict()
    error_dict['error_code'] = 1
    error_dict['error_msg'] = 'Unknown error'
    error_dict['http_status_code'] = http_status_code
    return error_dict

def success_dict(http_status_code=200):
    success_dict = _response_dict()
    success_dict['error_code'] = 0
    success_dict['error_msg'] = ''
    success_dict['http_status_code'] = http_status_code
    return success_dict

def render_template(request, context_dict, template, verbose=False, minify=True):
    http_status = context_dict['http_status_code'] or 200
    return render(request, template, context_dict, status=http_status)

def render_json(request, json_values, verbose=False, minify=True):
    http_status = json_values['http_status_code']
    encode = model_encode
    if verbose:
        encode = model_encode_verbose

    response_data = json.dumps(json_values, default=encode)
    return HttpResponse(response_data, content_type="application/json", status=http_status)

###
### PRIVATE
###

def _response_dict():
    response_dict = {}
    response_dict['error_code'] = 0
    response_dict['error_msg'] = ''
    response_dict['http_status_code'] = 200
    return response_dict