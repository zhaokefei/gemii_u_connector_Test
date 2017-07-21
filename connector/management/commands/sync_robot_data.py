#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import logging
from connector import apis
from django.core.management.base import BaseCommand
from connector.models import URobotModel
from django.db import transaction
import datetime
import time

sql_log = logging.getLogger("sql")

class Command(BaseCommand):
    """
    **同步机器人数据**

    **参数**

    """

    @transaction.atomic()
    def handle(self, *args, **options):
            """
                "vcSerialNo": "201703291010000001",
                "nChatRoomCount": "3",
                "vcNickName": "小U管家~技术0",
                "vcBase64NickName": "5bCPVeeuoeWutn7mioDmnK8w",
                "vcHeadImages": "http://wx.qlogo.cn/mmhead/ver_1/M9FMljmImEyvykCJGTrfib0cH2AVDMLqXRKnMbMibuWwd1Sic42ibyZ7z90xy1XKGzd6MKBsIUDwPturYF5Wcj1SEib1s1MVYsdMhBDMBZlBozkI/132",
                "vcCodeImages": "http://picture.ewemai.com/kc/20161110/qr_8e40651ae727bb8dc484f4ef6fda6d95.png",
                "nStatus": "14"
            }
            """
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql_log.info('start sync robot data(%s)' % now)
            response = json.loads(apis.get_robot_list())
            if int(response['nResult']) == -1:
                sql_log.info(response)
            else:
                datas = response['Data'][0]['RobotInfo']

                finish_count = 0
                fault_count = 0

                for data in datas:
                    vcSerialNo = data['vcSerialNo']
                    nChatRoomCount = data['nChatRoomCount']
                    vcNickName = data['vcNickName']
                    vcBase64NickName = data['vcBase64NickName']
                    vcHeadImages = data['vcHeadImages']
                    vcCodeImages = data['vcCodeImages']
                    nStatus = data['nStatus']

                    try:
                        robot = URobotModel.objects.get(vcSerialNo=vcSerialNo)
                    except URobotModel.DoesNotExist:
                        robot = URobotModel()
                        robot.vcSerialNo = vcSerialNo
                    robot.nChatRoomCount = nChatRoomCount
                    robot.vcNickName = vcNickName
                    robot.vcBase64NickName = vcBase64NickName
                    robot.vcHeadImages = vcHeadImages
                    robot.vcCodeImages = vcCodeImages
                    robot.nStatus = nStatus

                    robot.save()
                    finish_count += 1

                sql_log.info('finish_count data %s ' % finish_count)
                sql_log.info('fault_count data %s ' % fault_count)