# /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import json
import string
import random
import logging
import threading

import redis
import requests

import apis
from django.core import signals

from wechat.models import WeChatRoomMessageGemii

CODE_STR = string.ascii_letters + string.digits
django_log = logging.getLogger('message')


class DataReceiveThread(threading.Thread):
    def __init__(self, name, conf):
        threading.Thread.__init__(self)
        host = conf['host']
        port = conf['port']
        password = conf['password']
        db = conf['db']
        self.type = conf['type']
        self.name = name
        self.redis = redis.StrictRedis(host=host, port=port, password=password, db=db)
        self.ps = self.redis.pubsub()

        self.channel_sub = '20170630_'
        self.channel_pub = 'p20170701_'

    def run(self):
        django_log.info('启动线程名为 %s' % str(self.name))
        self.process()
        django_log.info('stop')

    def stop(self):
        self.ps.unsubscribe()

    def process(self):
        """
        监听redis, 调用由创接口发送消息
        :return:
        """
        # 订阅收消息频道
        self.ps.subscribe(self.channel_sub)
        # 监听频道
        for data in self.ps.listen():
            # 请求前发送信号
            signals.request_started.send(sender=self)
            # 获取redis数据, 出错重启apache2
            if data['type'] == 'message':
                robot_msg, send_msg = self.get_msg_data(data)
                django_log.info('马上要进入由创接口调用')
                # 调用由创接口，超时调用三次
                response = self.send_message(**send_msg)
                django_log.info('由创发送消息返回码------> %s' % str(response))
                # 存数据至mysql
                self.insert_msg_to_database(response, robot_msg)

            # 请求后发送信号
            signals.request_finished.send(sender=self)

    def insert_msg_to_database(self, response, robot_msg):
        response_data = json.loads(response)
        if str(response_data['nResult']) == "1":
            if self.type == 'A':
                django_log.info('开始进入A库存数据')
                WeChatRoomMessageGemii.objects.create(**robot_msg)
                django_log.info('库A数据插入完成')
                self.redis.publish(self.channel_pub, json.dumps(robot_msg))
            # elif self.type == 'B':
            else:
                django_log.info('开始进入B库存数据')
                WeChatRoomMessageGemii.objects.using('gemii_b').create(**robot_msg)
                django_log.info('库B数据插入完成')
                self.redis.publish(self.channel_pub, json.dumps(robot_msg))
        else:
            django_log.info('消息存库失败------>由创返回码为 %s' % str(response))

    def get_msg_data(self, data):
        request_data = json.loads(data['data'])
        # # 解析数据
        msg_data = request_data['Msg']
        django_log.info('获取到java数据------------> %s' % msg_data)
        try:
            vcChatRoomSerialNo = msg_data['u_roomId']
            nIsHit = msg_data['atAll']
            nMsgType = request_data['MsgType']
            vcWeixinSerialNo = ','.join(msg_data['memberIds'])
            msgContent = msg_data['Content']
            FileName = msg_data['FileName']
            RoomID = msg_data['RoomID']
            UserNickName = msg_data['UserNickName']
            CreateTime = time.strftime('%Y-%m-%d %H:%M:%S')
            MsgId = ''.join(random.sample(CODE_STR, random.randint(20, 24)))
        except Exception, e:
            django_log.info('发送消息参数错误 %s ' % e)

        robot_msg = {
            "Content": msgContent,
            "MsgType": 47 if nMsgType == 2 else nMsgType,
            "AppMsgType": 0,
            "UserDisplayName": UserNickName,
            "MsgId": MsgId,
            "CreateTime": CreateTime,
            "RoomID": RoomID,
            "MemberID": "",
            "UserNickName": UserNickName
        }

        django_log.info('生成发送给java的数据-----------> %s' % robot_msg)

        django_log.info('开始导入Chatroommodel')
        from models import ChatRoomModel
        django_log.info('导入Chatroommodel成功')
        record = ChatRoomModel.objects.filter(vcChatRoomSerialNo=vcChatRoomSerialNo)
        django_log.info('开始通过群编号查找对应的机器人')
        if record.exists():
            vcRobotSerialNo = record.first().vcRobotSerialNo
            django_log.info('获取到机器人编号')
        else:
            django_log.info('机器人编号记录不存在')

        msgtype_map = {1: '2001', 2: '2002', 3: '2005'}
        send_msg = {
            'vcChatRoomSerialNo': vcChatRoomSerialNo,
            'vcRobotSerialNo': vcRobotSerialNo,
            'nIsHit': nIsHit,
            'vcWeixinSerialNo': vcWeixinSerialNo,
            'nMsgType': msgtype_map.get(int(nMsgType)),
            'msgContent': msgContent,
            'vcTitle': FileName,
            'vcHref': msgContent.encode('utf8')
        }

        return robot_msg, send_msg

    def send_message(self, release=3, **kwargs):
        try:
            django_log.info('开始调用由创发消息接口')
            response = apis.send_chat_message(**kwargs)
            django_log.info('发送消息接口调用成功')
        except requests.exceptions.Timeout, e:
            django_log.info('连接超时 %s' % str(e.message))
            if release > 0:
                django_log.info('重新连接')
                return self.send_message(release-1, **kwargs)
            else:
                django_log.info('请求超时3次')

        return response

