# coding:utf-8
'''
Created on 2017年5月31日

@author: hepeng
'''
import logging
import json
import copy
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
        serializer = LegacyChatRoomMessageSerializer(instance)
        send_msg_data = copy.copy(serializer.data)
        save_msg_data = copy.copy(serializer.data)
        save_msg_data.pop('isLegal')
        try:
            record = ChatRoomModel.objects.get(vcChatRoomSerialNo=u_roomid)
            # B库存储
            if record.serNum == 'A':
                # 需要存数据库至A库
                WeChatRoomMessageGemii.objects.create(**save_msg_data)

                # 发送至A的redis
                connect_pool_a = connect_pool(settings.REDIS_CONFIG['redis_a'])
                publisher = redis.Redis(connection_pool=connect_pool_a)
                publisher.publish('p20170701_', json.dumps(send_msg_data))
            # elif record.serNum == 'B':
            else:
                # 需要存数据至B库
                WeChatRoomMessageGemii.objects.using('gemii_b').create(**save_msg_data)
                # django_log.info('serialiser B库----- %s' % str(serializer.data))

                # 发送至B的redis
                connect_pool_b = connect_pool(settings.REDIS_CONFIG['redis_b'])
                publisher = redis.Redis(connection_pool=connect_pool_b)
                publisher.publish('p20170701_', json.dumps(send_msg_data))

        except Exception, e:
            django_log.info('fail message %s' % e.message)


