# coding:utf-8
'''
Created on 2017年5月31日

@author: hepeng
'''
import json
import redis
import logging
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

from connector.models import ChatMessageModel, MemberInfo, IntoChatRoomMessageModel, ChatRoomModel
from .serializers import LegacyChatRoomMessageSerializer
from connector import apis
from connector.utils.mysql_db import MysqlDB
from connector.utils.db_config import DBCONF

# connect redis
pool = redis.ConnectionPool(host='54.223.198.95', port=8081, db=0, password="gemii@123.cc")
# pool = redis.ConnectionPool(host='gemii-jbb.ldtntv.ng.0001.cnn1.cache.amazonaws.com.cn', port=6379, db=0)
django_log = logging.getLogger('django')


# signal
@receiver(post_save, sender=ChatMessageModel)
def pub_message(sender, instance=None, created=False, **kwargs):
    if created:
        serializer = LegacyChatRoomMessageSerializer(instance)
        mysql = MysqlDB(DBCONF.wechat_gemii_config)
        try:
            mysql.insert('WeChatRoomMessage', serializer.data)
        finally:
            mysql.close()
            
        publisher = redis.Redis(connection_pool=pool)
        publisher.publish('p20170701_', json.dumps(serializer.data))


# 批量开群
@receiver(post_save, sender=IntoChatRoomMessageModel)
def intochatroom(sender, instance=None, created=False, **kwargs):
    if created:
        vcSerialNo = instance.vcSerialNo
        django_log.info(u'触发批量开群接口')
        apis.open_chatroom(vcSerialNo)

# 激活消息处理
@receiver(post_save, sender=ChatRoomModel)
def rece_msg(sender, instance=None, created=False, **kwargs):
    if created:
        vcChatRoomSerialNo = instance.vcChatRoomSerialNo
        django_log.info(u'触发激活消息处理接口')
        apis.recive_msg_open(vcChatRoomSerialNo)
