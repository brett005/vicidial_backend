import os
import requests
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from .utils import make_request_to_1c

api = Blueprint('api', __name__)
allowed_actions = ('send_sms', 'get_payment_requsits', 'get_main_info', 'get_loan_info', 'get_ticket_info',
                   'get_detail_loan', 'get_detail_ticket', 'find_by_fio')
another_actions = ('get_lk_info',)


@api.route('/ivr', methods=['GET', 'POST'])
@cross_origin()
def get_ivr_info():
    auth_key = request.headers.get('X-Auth-Key', '')
    if auth_key != os.environ.get('AUTH_KEY'):
        return jsonify(error='Not authenticated')
    phone = request.args.get('phone')
    send_sms = bool(request.args.get('sendsms', False))
    if phone:
        response = make_request_to_1c('ivr', {'phone': phone, 'send_sms': send_sms})
        return jsonify(response)
    return jsonify(error='phone is undefined')


@api.route('/vicidial/<action>', methods=['POST'])
@cross_origin()
def vicidial_handler(action):
    auth_key = request.headers.get('X-Auth-Key', '')
    if auth_key != os.environ.get('AUTH_KEY'):
        return jsonify(error='Not authenticated')

    try:
        data = request.get_json()
    except:
        return jsonify(error='data not json')

    data['action'] = action
    if action in allowed_actions:
        response = make_request_to_1c('vicidial', data)
    elif action in another_actions:
        gt_token = os.environ.get('AUTH_GETAWAY_TOKEN')
        gt_url = os.environ.get('GETAWAY_URL')
        data = {
            'flag_get': 'get_info_vici',
            'inn': data.get('inn', ''),
            'phone': data.get('phone', ''),
        }
        response = requests.post(gt_url, json=data, headers={'token': gt_token}, verify=False).json()
    else:
        response = {'error': 'method not allowed'}
    return jsonify(response)
