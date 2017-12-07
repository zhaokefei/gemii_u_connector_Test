# /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import json

import apis


class AIRobot(object):

    def __init__(self, robot_id='C6C612A0F755EA449275DD9C3E057F54',
                 room_id='5E95FD246CF899AA2AFF029022F75217'):
        self.robot_id = robot_id
        self.room_id = room_id
        self.content = None

    def send_message(self):
        apis.send_chat_message(vcChatRoomSerialNo=self.room_id,
                               vcRobotSerialNo=self.robot_id,
                               msgContent=self.content)

    def transfer_master_callback(self, task_id, u_roomid, room_name, u_userid, code, desc):
        content = ('转移群主回调结果如下: \n'
                   '结果码: %s\n'
                   '描述: %s\n'
                   '任务ID: %s\n'
                   '群名: %s\n'
                   '群编号: %s\n'
                   '新群主编号: %s\n' % (code, desc, task_id, room_name, u_roomid, u_userid))
        self.content = content

