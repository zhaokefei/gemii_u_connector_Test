# coding:utf-8
'''
Created on 2017年5月31日

@author: hepeng
'''
import logging
import json
import redis
from django.conf import settings
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

from connector.models import ChatMessageModel, IntoChatRoomMessageModel
from legacy_system.serializers import LegacyChatRoomMessageSerializer
from connector import apis
from connector.models import ChatRoomModel

from wechat.models import WeChatRoomMessageGemii


def connect_pool(conf):
    host = conf['host']
    port = conf['port']
    password = conf['password']
    db = conf['db']
    pool = redis.ConnectionPool(host=host, port=port, password=password, db=db)
    return pool

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
            if record.serNum == 'A':
                # 需要存数据库至A库
                django_log.info('即将存入B库')
                WeChatRoomMessageGemii.objects.create(**serializer.data)
                django_log.info('存储至 A库数据----- %s' % str(serializer.data))

                # 发送至A的redis
                django_log.info('发送消息至A库Redis')
                connect_pool_a = connect_pool(settings.REDIS_CONFIG['redis_a'])
                publisher = redis.Redis(connection_pool=connect_pool_a)
                publisher.publish('p20170701_', json.dumps(serializer.data))
            # elif record.serNum == 'B':
            else:
                # 需要存数据至B库
                django_log.info('即将存入B库')
                django_log.info('serialiser B库----- %s' % str(serializer.data))
                WeChatRoomMessageGemii.objects.using('gemii_b').create(**serializer.data)
                # django_log.info('serialiser B库----- %s' % str(serializer.data))

                # 发送至B的redis
                django_log.info('发送消息至B库Redis')
                connect_pool_b = connect_pool(settings.REDIS_CONFIG['redis_b'])
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
