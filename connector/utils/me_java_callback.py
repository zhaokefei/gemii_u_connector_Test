#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import logging
import json
from django.conf import settings
from wyeth.models import UserInfo
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UConnector.settings")


member_log = logging.getLogger('member')

def into_room_callback(open_id, room_id, time):
    try:
        callback_java_me_data = {
            'openID': open_id,
            'uRoomID': room_id,
            'time': time,
        }
        headers = {'content-type': 'application/json'}
        data = json.dumps(callback_java_me_data)
        java_rsp = requests.post(settings.INTO_ROOM_CALLBACK_JAVA_ME, data=data, headers=headers)
        member_log.info('java_rsp')
        member_log.info(java_rsp.text)
        return java_rsp.text
    except Exception, e:
        member_log.info('jave request error')
        member_log.info(e)


def drop_room_callback(open_id, room_id, time):
    try:
        callback_java_me_data = {
            'openID': open_id,
            'uRoomID': room_id,
            'time': time,
        }
        headers = {'content-type': 'application/json'}
        data = json.dumps(callback_java_me_data)
        java_rsp = requests.post(settings.DROP_ROOM_CALLBACK_JAVA_ME, data=data, headers=headers)
        member_log.info('java_rsp')
        member_log.info(java_rsp.text)
        return java_rsp.text
    except Exception, e:
        member_log.info('jave request error')
        member_log.info(e)


def get_openid_by_roomid_and_userid(roomid, userid):
    userinfos = UserInfo.objects.filter(MatchGroup=roomid, U_UserID=userid)
    if userinfos.exists():
        return userinfos[0].Openid
    else:
        return ''


