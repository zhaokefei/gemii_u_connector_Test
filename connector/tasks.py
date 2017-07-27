#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
from celery.task import task
from connector.models import RobotChatRoom

celery_log = logging.getLogger('celery')


@task
def handle_robotchatroom(vcrobotserialno, datas, nodatas):
    create_list = []
    up_nodata_count = 0
    up_data_count = 0
    for nodata in nodatas:
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
    return vcrobotserialno, up_data_count, up_nodata_count


