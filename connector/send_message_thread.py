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

from connector.models import ChatMessageModel
from wechat.models import WeChatRoomMessageGemii

CODE_STR = string.ascii_letters + string.digits
django_log = logging.getLogger('message')


class DataReceiveThread(threading.Thread):
    _running = False

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
        self._running = False
        self.ps.unsubscribe()

    def process(self):
        """
        监听redis, 调用由创接口发送消息
        :return:
        """
        # 订阅收消息频道
        self._running = True
        while self._running:
            try:
                self.ps.subscribe(self.channel_sub)
                # 监听频道
                for data in self.ps.listen():
                    # 请求前发送信号
                    signals.request_started.send(sender=self)
                    # 获取redis数据, 出错重启apache2
                    if data['type'] == 'message':
                        robot_msg, send_msg, save_conn_msg = self.get_msg_data(data)
                        if not (robot_msg and send_msg and save_conn_msg):
                            django_log.info('取数据时出错，进入下一条消息')
                            continue
                        django_log.info('马上要进入由创接口调用')
                        # 调用由创接口，超时调用三次
                        response = self.send_message(**send_msg)
                        if not response:
                            django_log.info('请求超时三次, 自动跳过该消息')
                            continue
                        django_log.info('由创发送消息返回码------> %s' % str(response))
                        # 存数据至mysql
                        self.insert_msg_to_database(response, robot_msg, save_conn_msg)
                # 请求后发送信号
                signals.request_finished.send(sender=self)
            except Exception, e:
                django_log.error(e)
                time.sleep(2)
                django_log.info('重新连接')

    def insert_msg_to_database(self, response, robot_msg, save_conn_msg):
        response_data = json.loads(response)
        if str(response_data['nResult']) == "1":
            if self.type == 'A':
                django_log.info('开始进入A库存数据')
                WeChatRoomMessageGemii.objects.create(**robot_msg)
                ChatMessageModel.objects.create(**save_conn_msg)
                django_log.info('库A数据插入完成')
                robot_msg['isLegal'] = "1"
                self.redis.publish(self.channel_pub, json.dumps(robot_msg))
            # elif self.type == 'B':
            else:
                django_log.info('开始进入B库存数据')
                WeChatRoomMessageGemii.objects.using('gemii_b').create(**robot_msg)
                ChatMessageModel.objects.create(**save_conn_msg)
                django_log.info('库B数据插入完成')
                robot_msg['isLegal'] = "1"
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
            RoomID = msg_data['RoomID']
            UserNickName = msg_data['UserNickName']
            MonitorSend = msg_data.get('MonitorSend', "")
            CreateTime = time.strftime('%Y-%m-%d %H:%M:%S')
            MsgId = ''.join(random.sample(CODE_STR, random.randint(20, 24)))
        except Exception, e:
            django_log.info('发送消息参数错误 %s ' % e)
            return False, False, False

        link = {}
        if nMsgType == 3:
            card_link = msgContent.split('#$#')
            link['vcTitle'] = card_link[0]
            link['vcDesc'] = card_link[1]
            link['vcHref'] = card_link[2]
            link['msgContent'] = card_link[2]
        # 发送给java的类型转换
        robot_type = {2: 47, 3: 50, 1: 1}
        # 发送给java的数据
        robot_msg = {
            "Content": msgContent,
            "MsgType": robot_type.get(nMsgType),
            "AppMsgType": 0,
            "UserDisplayName": UserNickName,
            "MsgId": MsgId,
            "CreateTime": CreateTime,
            "RoomID": RoomID,
            "MemberID": MonitorSend,
            "UserNickName": UserNickName
        }

        django_log.info('生成发送给java的数据-----------> %s' % robot_msg)

        from models import ChatRoomModel
        record = ChatRoomModel.objects.filter(vcChatRoomSerialNo=vcChatRoomSerialNo)
        django_log.info('开始通过群编号查找对应的机器人')
        if record.exists():
            vcRobotSerialNo = record.first().vcRobotSerialNo
            django_log.info('获取到机器人编号')
        else:
            django_log.info('机器人编号记录不存在')
            return False, False, False
        # 生成发送给由创的数据类型
        msgtype_map = {1: '2001', 2: '2002', 3: '2005'}
        # 发送给由创的消息
        send_msg = {
            'vcChatRoomSerialNo': vcChatRoomSerialNo,
            'vcRobotSerialNo': vcRobotSerialNo,
            'nIsHit': nIsHit,
            'vcWeixinSerialNo': vcWeixinSerialNo,
            'nMsgType': msgtype_map.get(int(nMsgType)),
            'msgContent': link.get('msgContent', msgContent),
            'vcTitle': link.get("vcTitle", ""),
            'vcDesc': link.get("vcDesc", ""),
            'vcHref': link.get("vcHref", "")
        }

        save_conn_msg = {
            "vcSerialNo": MsgId,
            "vcChatRoomSerialNo": vcChatRoomSerialNo,
            "vcFromWxUserSerialNo": vcRobotSerialNo,
            "dtMsgTime": CreateTime,
            "nMsgType": msgtype_map.get(int(nMsgType)),
            "vcContent": link.get('msgContent', msgContent),
            "vcShareTitle": link.get("vcTitle", ""),
            "vcShareDesc": link.get("vcDesc", ""),
            "vcShareUrl": link.get("vcHref", ""),
        }

        return robot_msg, send_msg, save_conn_msg

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
                return False

        return response

