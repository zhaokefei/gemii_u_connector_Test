#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
from celery.task import task
from connector.models import RobotChatRoom
from decorate import view_exception_handler
celery_log = logging.getLogger('celery')
django_log = logging.getLogger('django')

# @view_exception_handler
@task
def handle_robotchatroom(vcrobotserialno, datas, nodatas):
    create_list = []
    up_nodata_count = 0
    up_data_count = 0

    for nodata in nodatas:
        RobotChatRoom.objects.update_or_create()
        robot_chatroom = RobotChatRoom.objects.filter(vcRobotSerialNo=vcrobotserialno,
                                                      vcChatRoomSerialNo=nodata['vcChatRoomSerialNo'])
        if robot_chatroom.exists():
            robot_chatroom.update(state='0')
            up_nodata_count += 1
        else:
            create_list.append(
                RobotChatRoom(vcRobotSerialNo=vcrobotserialno, vcChatRoomSerialNo=nodata['vcChatRoomSerialNo'],
                              state='0'))

    for data in datas:
        robot_chatroom = RobotChatRoom.objects.filter(vcRobotSerialNo=vcrobotserialno,
                                                      vcChatRoomSerialNo=data['vcChatRoomSerialNo'])
        if robot_chatroom.exists():
            robot_chatroom.update(state='1')
            up_data_count += 1
        else:
            create_list.append(
                RobotChatRoom(vcRobotSerialNo=vcrobotserialno, vcChatRoomSerialNo=data['vcChatRoomSerialNo'],
                              state='1'))
    if create_list:
        RobotChatRoom.objects.bulk_create(create_list)
    django_log.info('更新机器人群信息')
    return vcrobotserialno, up_data_count, up_nodata_count


