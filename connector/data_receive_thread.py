#-*- coding: utf-8 -*-

import threading
import json
import string
import time
import random
import Queue
import redis
import logging
import apis
from connector.utils.mysql_db import MysqlDB
from connector.utils.db_config import DBCONF

CODE_STR = string.ascii_letters + string.digits
django_log = logging.getLogger('message')


class DataReceiveThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # self.redis = redis.StrictRedis(host='gemii-jbb.ldtntv.ng.0001.cnn1.cache.amazonaws.com.cn', port=6379, db=0)
        self.redis = redis.StrictRedis(host='54.223.198.95', port=8081, db=0, password="gemii@123.cc")

        self.channel_sub = '20170630_'
        self.channel_pub = 'p20170701_'

    def run(self):
        django_log.info('run method')
        self.process()

    def process(self):
        ps = self.redis.pubsub()

        ps.subscribe(self.channel_sub)
        django_log.info('发送消息线程为:%s ' % threading.current_thread())
        for data in ps.listen():
            if data['type'] == 'message':
                request_data = json.loads(data['data'])

                # # 解析数据
                msg_data = request_data['Msg']
                print 'msg_data------------>%s' % msg_data
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
                    continue

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
                    continue

                if int(nMsgType) == 1:
                    nMsgType= "2001"
                    response = apis.send_chat_message(vcChatRoomSerialNo=vcChatRoomSerialNo,
                                                      vcRobotSerialNo=vcRobotSerialNo,
                                                      nIsHit=nIsHit,
                                                      vcWeixinSerialNo=vcWeixinSerialNo,
                                                      nMsgType=nMsgType,
                                                      msgContent=msgContent)
                    django_log.info('文本消息发送接口调用')
                elif int(nMsgType) == 2:
                    nMsgType = "2002"
                    response = apis.send_chat_message(vcChatRoomSerialNo=vcChatRoomSerialNo,
                                                      vcRobotSerialNo=vcRobotSerialNo,
                                                      nIsHit=nIsHit,
                                                      vcWeixinSerialNo=vcWeixinSerialNo,
                                                      nMsgType=nMsgType,
                                                      msgContent=msgContent)
                    django_log.info('图片消息接口调用')

                elif int(nMsgType) == 3:
                    nMsgType = "2005"
                    response = apis.send_chat_message(vcChatRoomSerialNo=vcChatRoomSerialNo,
                                                      vcRobotSerialNo=vcRobotSerialNo,
                                                      nIsHit=nIsHit,
                                                      vcWeixinSerialNo=vcWeixinSerialNo,
                                                      nMsgType=nMsgType,
                                                      msgContent=msgContent,
                                                      vcTitle=FileName,
                                                      vcHref=msgContent)
                django_log.info('正在获取由创消息返回码')
                django_log.info('由创发送消息返回码------> %s' % str(response))
                django_log.info('由创消息返回码打印完成')
                response_data = json.loads(response)
                if str(response_data['nResult']) == "1":
                    django_log.info('开始进入存数据')
                    mysql_wechat_gemii = MysqlDB(DBCONF.wechat_gemii_config)
                    try:
                        mysql_wechat_gemii.insert('WeChatRoomMessage', robot_msg)
                        django_log.info('插入wechatroommessage数据 %s' % robot_msg)
                    except Exception, e:
                        django_log.info('数据插入错误 %s' % e.message)
                    finally:
                        mysql_wechat_gemii.close()
                    self.redis.publish(self.channel_pub, json.dumps(robot_msg))
                else:
                    django_log.info('消息存库失败------>由创返回码为 %s' % str(response))
            else:
                django_log.info('未处理%s ' % str(data))

        django_log.info('这是一个线程')
