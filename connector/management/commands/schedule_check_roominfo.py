# /usr/bin/env python
# -*- coding:utf-8 -*-

import json
import random
import time
import logging

from connector import apis
from django.core.management.base import BaseCommand
from connector.models import ChatRoomModel
from wechat.models import WeChatRoomInfoGemii
from wyeth.models import WeChatRoomInfo

sql_log = logging.getLogger("sql")

"""
    vcChatRoomSerialNo = models.CharField(max_length=50, unique=True, verbose_name=u'群编号')
    vcName = models.CharField(max_length=50, verbose_name=u'群昵称')
    vcBase64Name = models.CharField(max_length=100, verbose_name=u'base64编码后的群昵称')
    vcWxUserSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'开群用户编号')
    vcWxManagerUserSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'群主的微信用户编号')
    vcRobotSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'机器人编号')
    vcApplyCodeSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'验证码编号')
"""

class Command(BaseCommand):

    """
    **导入群信息数据**

    **参数**

    """
    # @transaction.atomic()
    def handle(self, *args, **options):

        # # 获取机器人列表
        robot_list_data = self.get_robot_list()

        if not robot_list_data:
            return
        #
        qun_total = 0
        insert_num = 0

        for robot in robot_list_data:
            # 获取机器人编号和名称,及机器人二维码
            robot_num = robot['vcSerialNo']
            robot_name = robot['vcNickName']

            # 获取机器人所对应的群列表
            try:
                room_list = json.loads(apis.get_chatroom_list(str(robot_num)), strict=False)
            except Exception, e:
                # 错误的机器人编号，未匹配到对应的群
                sql_log.info(u'错误编号：%s, 对应的机器人 %s' % (e.message, robot_num))
                continue
            # 机器人没有群信息
            if not room_list['Data'][0]:
                sql_log.info(u"机器人 %s 所对应的群为空: %s" % (robot_num, room_list))
                continue

            # 写入群信息
            for room in room_list['Data'][0]['ChatRoomData']:
                qun_total += 1
                vcChatRoomSerialNo = room['vcChatRoomSerialNo']
                vcWxUserSerialNo = room['vcWxUserSerialNo']
                vcName = room['vcName']
                vcBase64Name = room['vcBase64Name']
                vcRobotSerialNo = robot_num

                # 根据 群编号 先查询数据里是否 有群信息
                record = ChatRoomModel.objects.filter(vcChatRoomSerialNo=vcChatRoomSerialNo)
                # 找到A库对应的 群
                # record2wechat = WeChatRoomInfoGemii.objects.using('gemii').filter(U_RoomID=vcChatRoomSerialNo)
                # record2wyeth = WeChatRoomInfo.objects.using('wyeth').filter(U_RoomID=vcChatRoomSerialNo)

                # 如果 这个群 不存在 添加
                if not record.exists():
                    insert_num += 1
                    sql_log.info(u'插入数据 群编号:%s, 机器人编号:%s, 群名: %s' % (vcChatRoomSerialNo, vcRobotSerialNo, vcName))
                    new_record = ChatRoomModel(vcChatRoomSerialNo=vcChatRoomSerialNo, vcWxUserSerialNo=vcWxUserSerialNo,
                                               vcName=vcName, vcBase64Name=vcBase64Name, vcRobotSerialNo=vcRobotSerialNo)

                    # 修改数据库后 跟新保存
                    new_record.save()
                else:
                    count = record.count()
                    if count == 1:
                        record.update(vcName=vcName, vcBase64Name=vcBase64Name,
                                      vcRobotSerialNo=robot_num, vcWxUserSerialNo=vcWxUserSerialNo)

                try:
                    # 跟新 群成员
                    res_data = apis.receive_member_info(vcChatRoomSerialNo)
                    sql_log.info(res_data)

                    # 跟新 A库的 群昵称 (如果存在  再更新)
                    # if record2wechat.exists():
                    #     record2wechat.update(RoomName=vcName)
                    # if record2wyeth.exists():
                    #     record2wyeth.update(RoomName=vcName)
                    # sql_log.info(u'两个A库的群昵称更新完成')

                except Exception, e:
                    sql_log.info(u'获取群成员失败 %s' % vcChatRoomSerialNo)
                    sql_log.info(u'错误日志 %s' % e.message)

                time.sleep(3)

        sql_log.info(u'群总数为： %s' % qun_total)
        sql_log.info(u'插入群数据总数： %s' % insert_num)


    def get_robot_list(self, release=3, **kwargs):
        try:
            robot_list_response = apis.get_robot_list()
            robot_list_data = json.loads(robot_list_response)['Data'][0]['RobotInfo']
        except Exception, e:
            sql_log.info(u"获取机器人数据错误 %s" % e.message)
            if release > 0:
                sql_log.info(u'重新调用接口')
                return self.get_robot_list(release-1, **kwargs)
            else:
                sql_log.info(u'请求超时3次')
                return False

        return robot_list_data
