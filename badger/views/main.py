import logging

from django.shortcuts import render
from django.contrib.auth.models import User
from badger.views.response import *
from badger.logic.badgetypes import BADGE_TYPES
import badger.apis.models.badge as badge_api

def bootstrap(request):
    logging.warn('bootstrap')
    response_dict = success_dict()
    return render_json(request, response_dict)

def clear(request):
    logging.warn('clear')
    username = request.GET['username']
    badge_type = request.GET['badge_type']

    if not username:
        response_dict = error_dict()
        response_dict['error_code'] = 100
        response_dict['error_msg'] = 'Missing username'
        return render_json(request, response_dict)

    if not badge_type:
        response_dict = error_dict()
        response_dict['error_code'] = 200
        response_dict['error_msg'] = 'Missing badge_type'
        return render_json(request, response_dict)

    logging.warn('fetching user')
    user = None
    try:
        user = User.objects.get(username=username)
    except:
        response_dict = error_dict()
        response_dict['error_code'] = 300
        response_dict['error_msg'] = 'No user'
        return render_json(request, response_dict)

    # delete the badges
    badge_api.delete_by_user_and_badge_type(user, badge_type)

    logging.warn('badge delete done')
    response_dict = success_dict()
    return render_json(request, response_dict)