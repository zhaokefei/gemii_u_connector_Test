# coding:utf-8
'''
Created on 2017年5月31日

@author: hepeng
'''
import logging
import json
import redis
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

from connector.models import ChatMessageModel, MemberInfo, IntoChatRoomMessageModel, ChatRoomModel
from legacy_system.serializers import LegacyChatRoomMessageSerializer
from connector import apis
from connector.models import ChatRoomModel
from connector.utils.mysql_db import MysqlDB
from connector.utils.db_config import DBCONF
from connector.utils.constant import MsgConf

# # 生产connect redis
# redis_b = MsgConf.redis_jbb_b
# redis_a = MsgConf.redis_wyeth_a
# 测试 redis
# redis_test = MsgConf.redis_test


def connect_pool(conf):
    host = conf['host']
    port = conf['port']
    password = conf['password']
    db = conf['db']
    pool = redis.ConnectionPool(host=host, port=port, password=password, db=db)
    return pool


# pool = redis.ConnectionPool(host='54.223.198.95', port=8081, db=0, password="gemii@123.cc")

django_log = logging.getLogger('django')

# signal
@receiver(post_save, sender=ChatMessageModel)
def pub_message(sender, instance=None, created=False, **kwargs):
    if created:
        u_roomid = instance.vcChatRoomSerialNo
        django_log.info('用户发消息对应的群编号 %s' % str(u_roomid))
        serializer = LegacyChatRoomMessageSerializer(instance)
        try:
            record = ChatRoomModel.objects.get(vcChatRoomSerialNo=u_roomid)
            # B库存储
            # TODO 需要用户发消息存库走redis修改
            if record.serNum == 'A':
                # 需要存数据库至A库，数据库地址为:
                wechat_a_gemii_mysql = MysqlDB(DBCONF.wechat_gemii_config)
                try:
                    wechat_a_gemii_mysql.insert('WeChatRoomMessage', serializer.data)
                finally:
                    wechat_a_gemii_mysql.close()
                django_log.info('存储至 A库数据----- %s' % str(serializer.data))

                # 发送至A的redis
                django_log.info('发送消息至A库Redis')
                connect_pool_a = connect_pool(MsgConf.redis_test)
                publisher = redis.Redis(connection_pool=connect_pool_a)
                publisher.publish('p20170701_', json.dumps(serializer.data))
            # elif record.serNum == 'B':
            else:
                # 需要存数据至B库，数据库地址为:
                wechat_b_gemii_mysql = MysqlDB(DBCONF.wechat_gemii_config)
                try:
                    wechat_b_gemii_mysql.insert('WeChatRoomMessage', serializer.data)
                finally:
                    wechat_b_gemii_mysql.close()
                django_log.info('serialiser B库----- %s' % str(serializer.data))

                # 发送至B的redis
                django_log.info('发送消息至B库Redis')
                connect_pool_b = connect_pool(MsgConf.redis_test)
                publisher = redis.Redis(connection_pool=connect_pool_b)
                publisher.publish('p20170701_', json.dumps(serializer.data))

        except Exception, e:
            django_log.info('用户发送消息，存储消息时出错，错误为: %s' % e.message)


# 批量开群
@receiver(post_save, sender=IntoChatRoomMessageModel)
def intochatroom(sender, instance=None, created=False, **kwargs):
    if created:
        vcSerialNo = instance.vcSerialNo
        django_log.info('批量开群 %s' % str(vcSerialNo))
        apis.open_chatroom(vcSerialNo)

# 激活消息处理
@receiver(post_save, sender=ChatRoomModel)
def rece_msg(sender, instance=None, created=False, **kwargs):
    if created:
        vcChatRoomSerialNo = instance.vcChatRoomSerialNo
        django_log.info('激活消息处理 %s' % str(vcChatRoomSerialNo))
        apis.recive_msg_open(vcChatRoomSerialNo)
