import logging

from django.shortcuts import render
from django.contrib.auth.models import User
from push_notifications.models import APNSDevice, GCMDevice
from lobot.views.response import *
from lobot.logic.messages import MESSAGES
from cca import settings
import badger.apis.models.badge as badge_api
from badger.logic.badgetypes import BADGE_TYPES

def bootstrap(request):
    logging.warn('bootstrap')

    user = None
    try:
        # andrew
        user = User.objects.get(username='ltrempe')
    except:
        logging.warn('no user')

    response_dict = success_dict()
    response_dict['user'] = user.first_name
    response_dict['gcm_api_key'] = settings.PUSH_NOTIFICATIONS_SETTINGS['GCM_API_KEY']
    response_dict['apns_cer_file'] = settings.PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE']
    return render_json(request, response_dict)


def register(request):
    logging.warn('register')
    os_type = get_request_var(request, 'os')
    username = get_request_var(request, 'username')
    registration_id = get_request_var(request, 'registration_id')

    if not username:
        response_dict = error_dict()
        response_dict['error_code'] = 100
        response_dict['error_msg'] = 'Missing username'
        return render_json(request, response_dict)

    if not registration_id:
        response_dict = error_dict()
        response_dict['error_code'] = 200
        response_dict['error_msg'] = 'Missing registration_id'
        return render_json(request, response_dict)

    if not os_type:
        response_dict = error_dict()
        response_dict['error_code'] = 300
        response_dict['error_msg'] = 'Missing os_type'
        return render_json(request, response_dict)

    logging.warn('fetching user')
    user = User.objects.get(username=username)
    if not user:
        response_dict = error_dict()
        response_dict['error_code'] = 400
        response_dict['error_msg'] = 'No user'
        return render_json(request, response_dict)

    if os_type == 'a':
        apns_device = None
        try:
            apns_device = APNSDevice.objects.get(user=user)
            logging.warn('apns device already registered')
        except:
            logging.exception('error getting apns device')
            logging.warn('no existing apns device')

        if apns_device:
            if registration_id != apns_device.registration_id:
                logging.warn('updating apns device with new registration_id')
                apns_device.registration_id = registration_id
                apns_device.save()
        else:
            logging.warn('creating apns device')
            try:
                apns_device = APNSDevice()
                apns_device.user = user
                apns_device.name = user.first_name
                apns_device.registration_id = registration_id
                apns_device.save()
            except:
                logging.exception('error creating apns device')
                response_dict = error_dict()
                response_dict['error_code'] = 500
                response_dict['error_msg'] = 'Error creating apns device'
                return render_json(request, response_dict)
    elif os_type == 'g':
        gcm_device = None
        try:
            gcm_device = GCMDevice.objects.get(user=user)
            logging.warn('gcm device already registered')
        except:
            logging.exception('error getting gcm device')
            logging.warn('no existing gcm device')

        if gcm_device:
            if registration_id != gcm_device.registration_id:
                logging.warn('updating gcm device with new registration_id')
                gcm_device.registration_id = registration_id
                gcm_device.save()
        else:
            logging.warn('creating gcm device')
            try:
                gcm_device = GCMDevice()
                gcm_device.user = user
                gcm_device.name = user.first_name
                gcm_device.registration_id = registration_id
                gcm_device.save()
            except:
                logging.exception('error creating gcm device')
                response_dict = error_dict()
                response_dict['error_code'] = 500
                response_dict['error_msg'] = 'Error creating gcm device'
                return render_json(request, response_dict)
    else:
        response_dict = error_dict()
        response_dict['error_code'] = 600
        response_dict['error_msg'] = 'Unrecognized os_type'
        return render_json(request, response_dict)

    logging.warn('registration done')
    response_dict = success_dict()
    return render_json(request, response_dict)

def push(request):
    logging.warn('push')
    username = get_request_var(request, 'username')
    namespace = get_request_var(request, 'namespace')
    message_num = get_request_var(request, 'message_num')

    if not username:
        response_dict = error_dict()
        response_dict['error_code'] = 100
        response_dict['error_msg'] = 'Missing username'
        return render_json(request, response_dict)

    if not namespace:
        response_dict = error_dict()
        response_dict['error_code'] = 200
        response_dict['error_msg'] = 'Missing namespace'
        return render_json(request, response_dict)

    if not message_num:
        response_dict = error_dict()
        response_dict['error_code'] = 300
        response_dict['error_msg'] = 'Missing message_num'
        return render_json(request, response_dict)

    logging.warn('fetching user')
    user = User.objects.get(username=username)
    if not user:
        response_dict = error_dict()
        response_dict['error_code'] = 400
        response_dict['error_msg'] = 'No user'
        return render_json(request, response_dict)

    message = None
    try:
        message = MESSAGES[namespace][message_num]
    except:
        logging.error('no message found for namespace: ' + namespace)
        response_dict = error_dict()
        response_dict['error_code'] = 500
        response_dict['error_msg'] = 'No message'
        return render_json(request, response_dict)

    logging.warn('fetching device')
    device = None

    try:
        device = APNSDevice.objects.get(user=user)
        logging.warn('found apns device')
    except:
        logging.error('no apns device found')

    if not device:
        try:
            device = GCMDevice.objects.get(user=user)
            logging.warn('found gcm device')
        except:
            logging.error('no gcm device found')

    if not device:
        logging.error('no device found')
        response_dict = error_dict()
        response_dict['error_code'] = 600
        response_dict['error_msg'] = 'No device found'
        return render_json(request, response_dict)

    # do badges
    logging.warn('entering badge')
    badge_api.create(user, BADGE_TYPES['message'])

    logging.warn('getting badge count')
    badge_count = badge_api.count_by_user(user)
    logging.warn('badge count: ' + str(badge_count))

    # create extra info
    extra = {}
    extra['message_num'] = message_num
    logging.warn('sending message: ' + message)
    device.send_message(message, badge=badge_count, extra=extra)

    response_dict = success_dict()
    response_dict['user'] = user.first_name
    response_dict['message'] = message
    return render_json(request, response_dict)