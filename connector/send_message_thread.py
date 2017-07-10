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

from connector.utils.mysql_db import MysqlDB
from connector.utils.db_config import DBCONF
from django.core import signals

CODE_STR = string.ascii_letters + string.digits
django_log = logging.getLogger('message')


# class DataReceive(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.redis = redis.StrictRedis(host='gemii-jbb.ldtntv.ng.0001.cnn1.cache.amazonaws.com.cn', port=6379, db=0)
#         # self.redis = redis.StrictRedis(host='54.223.198.95', port=8081, db=0, password="gemii@123.cc")
#         # self.redis = redis.StrictRedis(host='localhost', port=8081, db=0)
#
#         self.channel_sub = '20170630_'
#         self.channel_pub = 'p20170701_'

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
        # self.redis = redis.StrictRedis(host='54.223.198.95', port=8081, db=0, password="gemii@123.cc")

        self.channel_sub = '20170630_'
        self.channel_pub = 'p20170701_'

    def run(self):
        django_log.info('run method')
        self.process()

    def process(self):
        """
        监听redis, 调用由创接口发送消息
        :return:
        """
        # 订阅发布
        ps = self.redis.pubsub()
        # 订阅收消息频道
        ps.subscribe(self.channel_sub)
        # 监听频道
        for data in ps.listen():
            # 请求前发送信号
            signals.request_started.send(sender=self)
            # 获取redis数据, 出错重启apache2
            if data['type'] == 'message':
                robot_msg, send_msg = self.get_msg_data(data)
                django_log.info('马上要进入由创接口调用')
                # 调用由创接口，超时调用三次，否则重启apache2
                response = self.send_message(**send_msg)
                django_log.info('由创发送消息返回码------> %s' % str(response))
                # 存数据至mysql
                self.insert_msg_to_database(response, robot_msg)

            # 请求后发送信号
            signals.request_finished.send(sender=self)

    def insert_msg_to_database(self, response, robot_msg):
        response_data = json.loads(response)
        # if str(response_data['nResult']) == "1":
        #     django_log.info('开始进入存数据')
        #     mysql_wechat_gemii = MysqlDB(DBCONF.wechat_gemii_config)
        #     try:
        #         mysql_wechat_gemii.insert('WeChatRoomMessage', robot_msg)
        #         django_log.info('插入wechatroommessage数据 %s' % robot_msg)
        #     except Exception, e:
        #         django_log.info('数据插入错误 %s' % e.message)
        #     finally:
        #         mysql_wechat_gemii.close()
        #     self.redis.publish(self.channel_pub, json.dumps(robot_msg))
        # else:
        #     django_log.info('消息存库失败------>由创返回码为 %s' % str(response))
        if str(response_data['nResult']) == "1":
            if self.type == 'A':
                django_log.info('开始进入A库存数据')
                mysql_wechat_a_gemii = MysqlDB(DBCONF.wechat_gemii_config)
                try:
                    mysql_wechat_a_gemii.insert('WeChatRoomMessage', robot_msg)
                    django_log.info('插入wechatroommessage数据 %s' % robot_msg)
                except Exception, e:
                    django_log.info('数据插入错误 %s' % e.message)
                finally:
                    mysql_wechat_a_gemii.close()
                self.redis.publish(self.channel_pub, json.dumps(robot_msg))
            # elif self.type == 'B':
            else:
                django_log.info('开始进入B库存数据')
                mysql_wechat_b_gemii = MysqlDB(DBCONF.wechat_gemii_config)
                try:
                    mysql_wechat_b_gemii.insert('WeChatRoomMessage', robot_msg)
                    django_log.info('插入B库wechatroommessage数据 %s' % str(robot_msg))
                except Exception, e:
                    django_log.info('数据插入错误 %s' % e.message)
                finally:
                    mysql_wechat_b_gemii.close()
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
            # TODO 重启apache2
            os.system('sudo service apache2 reload')

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
            # TODO 重启apache2
            os.system('sudo service apache2 reload')

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
                import os
                os.system('sudo service apache2 reload')

        return response

