#!/usr/bin/env python

import json
import time
from datetime import datetime
from urllib.parse import quote_plus, urljoin

import requests
from requests import exceptions


class SmsAeroError(Exception):
    """ Super class of all SmsAero Errors. """


class SmsAeroHTTPError(SmsAeroError):
    """ A Connection error occurred. """


class SmsAeroConnectionError(SmsAeroError):
    """ A Connection error occurred. """


class SmsAero:
    GATE_URLS = [
        '@gate.smsaero.ru/v2/',
        '@gate.smsaero.org/v2/',
        '@gate.smsaero.net/v2/',
        '@gate.smsaero.uz/v2/',
    ]
    SIGNATURE = 'Sms Aero'
    TYPE_SEND = 2

    def __init__(
            self, email, api_key,
            url_gate=None,
            signature=SIGNATURE,
            type_send=TYPE_SEND
    ):
        self.email = email
        self.api_key = api_key

        self.url_gate = url_gate
        self.signature = signature
        self.type_send = type_send
        self.session = requests.session()

    def _get_gate_urls(self):
        if self.url_gate:
            return [self.url_gate]
        return self.GATE_URLS

    def _request(self, selector, data=None, page=None, proto='https'):
        try:
            for gate in self._get_gate_urls():
                try:
                    url = urljoin("{}://{}:{}{}".format(proto, quote_plus(self.email), self.api_key, gate), selector)
                    if page:
                        url = urljoin(url, "?page={}".format(page))
                    response = self.session.post(url, json=data or {})
                    return self._check_response(response.content)
                except exceptions.SSLError:
                    proto = 'http'
                    continue
                except exceptions.ConnectionError:
                    continue
            else:
                raise SmsAeroConnectionError
        except requests.RequestException as err:
            raise SmsAeroHTTPError(err)

    @staticmethod
    def _get_num(number):
        if type(number) is list:
            num = 'numbers'
        else:
            num = 'number'
            number = str(number)
        return [num, number]

    @staticmethod
    def _check_response(content):
        try:
            response = json.loads(content)
            if 'result' in response and response['result'] == 'reject':
                raise SmsAeroError(response['reason'])
            elif 'result' in response and response['result'] == 'no credits':
                raise SmsAeroError(response['result'])
            return response
        except ValueError:
            if 'incorrect language' in content:
                raise SmsAeroError("incorrect language in '...' use \
                    the cyrillic or roman alphabet.")
            else:
                raise SmsAeroError('unexpected format is received')

    def send(self, number, text, date_send=None, callback_url=None):
        num, number = self._get_num(number)
        data = {
            num: number,
            'sign': self.signature,
            'text': text,
            'callbackUrl': callback_url
        }
        if date_send is not None:
            if isinstance(date_send, datetime):
                data['dateSend'] = int(time.mktime(date_send.timetuple()))
            else:
                raise SmsAeroError('param `date` is not datetime object')
        return self._request('sms/send', data)

    def sms_status(self, sms_id):
        return self._request('sms/status', {'id': sms_id})

    def sms_list(self, number=None, text=None, page=None):
        data = {}
        if number:
            data.update({'number': str(number)})
        if text:
            data.update({'text': text})
        return self._request('sms/list', data, page)
