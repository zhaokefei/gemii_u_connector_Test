#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import json
import datetime
import time
import logging
from connector import apis
import base64

from django.conf import settings


message_log = logging.getLogger('message')


def save_json(filename, data, dirName, mode='a'):
    """
    @brief      Saves dict to json file.
    @param      filename  String
    @param      data      Dict
    @param      dirName   String
    @return     file path
    """
    # Log.debug('save json: ' + filename)
    fn = filename
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    fn = os.path.join(dirName, filename)

    with open(fn, mode) as f:
        f.write(json.dumps(data, indent=4) + '\n')
    return fn

def time_strf(time_str):
    if isinstance(time_str,unicode):
        time_str = time_str.encode('utf-8')
    datestr = time.strptime(time_str, '%Y/%m/%d %H:%M:%S')
    date_time = datestr[0:6]
    return datetime.datetime(*date_time)


def open_room(vcSerialNo):
    message_log.info('批量开群 %s' % str(vcSerialNo))
    rsp = apis.open_chatroom(vcSerialNo)
    return rsp

def rece_msg(u_roomid):
    # 激活消息处理
    message_log.info('激活消息处理 %s' % str(u_roomid))
    rsp = apis.recive_msg_open(u_roomid)
    return rsp

# 对 字符串进行 解密
def decode_base64(chars):
    if isinstance(chars, str):
        chars = chars.decode('utf-8').encode('utf8')
    if isinstance(chars, unicode):
        chars = chars.encode('utf8')
    return base64.urlsafe_b64decode(chars)

# 对 字符串进行 加密
def encode_base64(chars):
    if isinstance(chars, str):
        chars = chars.decode('utf-8').encode('utf8')
    if isinstance(chars, unicode):
        chars = chars.encode('utf8')
    return base64.urlsafe_b64encode(chars)

def emoji_to_unicode(nickname):
    import e4u
    e4u.load(filename=settings.EMOJI_TO_UNICODE)
    try:
        result = e4u.translate(nickname, **e4u.SOFTBANK_TRANSLATE_PROFILE)
    except Exception, e:
        message_log.info('translation name error: %s' % str(e.message))
        result = nickname
    return result


def get_robotQucode_fail(post, u_response):
    message = u"群二维码未获得,请查看：\n群名称:%s \ntask_id:%s \n错误信息为:%s" \
              % (post[u'group_name'], post[u'task_id'],  u_response[u'msg'])
    response = apis.send_chat_message(vcChatRoomSerialNo='5E95FD246CF899AA2AFF029022F75217',
                                      vcRobotSerialNo='C6C612A0F755EA449275DD9C3E057F54',
                                      vcWeixinSerialNo='',
                                      msgContent=message)

    message_log.info('robotQucode_fail message response %s' % str(response))
