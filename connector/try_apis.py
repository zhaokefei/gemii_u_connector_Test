# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import apis

# Create your tests here.
def create_chatroom_task_apis():
    response = apis.create_chatroom_task(
        theme=u"景栗测试流程群",
        introduce=u"景栗测试流程群景栗测试流程群",
        limit_member_count=50)
    print response
    return response

def active_chatroom_task_api():
    response = apis.active_chatroom_task(
        task_id=7344,
        theme="景栗测试流程群",
        theme_image="../Inc/PlatForm/images/temp/theme_0001.jpg",
        pay_count=1,
        creator="oDkzcvhEVRMjdMyiuzr79Jx3CLEk",
        create_time="2017-06-29T08:57:18.767")
    print response
    return response

def create_chatroom_api():
    response = apis.create_chatroom(7344)
    print response
    return response


def group_chatroom_id_api():
    response = apis.group_chatroom_id(7344)
    print response
    return response

def get_qrcode_api():
    response = apis.get_robot_qrcode(7344, "", "label_1", "group_1", "group_name", "719945BB4CE070B4B00384F59FC6D0F5")
    print response
    return response

def modify_roomname_api():
    response = apis.modify_chatroom_info(7215, "43BDAC6EC85F1045869AC282ADA43D6E",
                                         "栗子猫猫猫妈妈kkkln", "2017-06-27T10:05:50.47")
    print response
    return response

def get_msg_robot_qrcode_api():
    re = apis.get_qrcode()
    print re
    return re

def recive_msg_open_api():
    response = apis.recive_msg_open("719945BB4CE070B4B00384F59FC6D0F5")
    print response
    return response

def send_chat_message_api():
    response = apis.send_chat_message(vcChatRoomSerialNo="60E86581B156171EB9D588EF5E4D4C57", vcRobotSerialNo="2017061414475882333300000000064",
                                      nIsHit=0, nMsgType="2001", msgContent="大家好拉")
    print response
    return response

def receive_memeber_info_api():
    response = apis.receive_member_info("719945BB4CE070B4B00384F59FC6D0F5")
    print response
    return response

def get_chatroom_list_api():
    response = apis.get_chatroom_list("2017061414475882333300000000064")
    print response
    return response

if __name__ == '__main__':
    pass
    # create_chatroom_task_apis()

    # {
    #     "code": 0,
    #     "msg": "",
    #     "data": {
    #         "task_id": 7344,
    #         "theme": "景栗测试流程群",
    #         "theme_image": "../Inc/PlatForm/images/temp/theme_0001.jpg",
    #         "pay_count": 0,
    #         "is_paid": false,
    #         "creator": "oDkzcvhEVRMjdMyiuzr79Jx3CLEk",
    #         "create_time": "2017-06-29T08:57:18.767",
    #         "type": 12,
    #         "status": 11
    #     }
    # }

    # active_chatroom_task_api()

# {
#     "code": 0,
#     "msg": "",
#     "data": {
#         "task_id": 7344,
#         "theme": "景栗测试流程群",
#         "theme_image": "../Inc/PlatForm/images/temp/theme_0001.jpg",
#         "pay_count": 1,
#         "is_paid": true,
#         "creator": "oDkzcvhEVRMjdMyiuzr79Jx3CLEk",
#         "create_time": "2017-06-29T08:57:18.767",
#         "type": 12,
#         "status": 11
#     }
# }
#     create_chatroom_api()

    # {
    #     "code": 0,
    #     "msg": "",
    #     "data": {
    #         "wx_alias": "ygdtfguh",
    #         "qr_code": "http://picture.ewemai.com/kc/20170628/qr_296a73ed83aced5df90371569d4e361f.png",
    #         "verify_code": "2400",
    #         "wx_nickname": "直播`彗云",
    #         "head_img_url": "http://wx.qlogo.cn/mmhead/ver_1/owl15p1cm7Ncia1Fwx2hy8MhAtFB2pA4HEYNgg5OtoJc01Bd56NK1geuZ6X5p4Qxnugo63caW4ffl7KHwC3SiboBzVhXhhjgnbtbVTmON4s8g/96"
    #     }
    # }

    # group_chatroom_id_api()

# {
#     "code": 0,
#     "msg": "",
#     "data": [
#         {
#             "task_id": 7344,
#             "chat_room_id": "719945BB4CE070B4B00384F59FC6D0F5",
#             "chat_room_name": "景栗测试流程群-1",
#             "create_time": "2017-06-29T09:02:04.74",
#             "notice": ""
#         }
#     ]
# }

    # get_qrcode_api()

    # {
    #     "code": 0,
    #     "msg": "",
    #     "data": {
    #         "task_account": {
    #             "wx_alias": "txkeftu",
    #             "qr_code": "http://picture.ewemai.com/kc/20170622/qr_b2460c6459d490353330f21e0d4f7fb3.png",
    #             "verify_code": "1581",
    #             "wx_nickname": "助理#晨曦",
    #             "head_img_url": "http://wx.qlogo.cn/mmhead/PiajxSqBRaELbAxFbvBrmD7JEEJT3AI6KXaFdEfY8tJz5tH6yVBMFyA/96"
    #         },
    #         "task_id": 7344,
    #         "label_id": 0,
    #         "open_id": "label_1",
    #         "group_id": "group_1",
    #         "group_name": "group_name",
    #         "chat_room_id": "719945BB4CE070B4B00384F59FC6D0F5",
    #         "code": "code",
    #         "instance_id": ""
    #     }
    # }

    # modify_roomname_api()
    # {
    #     "code": 0,
    #     "msg": "",
    #     "data": {
    #         "task_id": 7215,
    #         "chat_room_id": "43BDAC6EC85F1045869AC282ADA43D6E",
    #         "chat_room_name": "栗子猫猫猫妈妈ha-3",
    #         "create_time": "2017-06-27T10:05:50.47",
    #         "notice": ""
    #     }
    # }

    # get_msg_robot_qrcode_api()
    # {
    #     "nResult": "1",
    #     "vcResult": "成功",
    #     "Data": [
    #         {
    #             "ApplyCodeData": [
    #                 {
    #                     "vcSerialNo": "201706291030000011",
    #                     "vcMerchantNo": "201706141010001",
    #                     "vcRobotSerialNo": "2017061414475882333300000000064",
    #                     "vcCode": "015",
    #                     "vcChatRoomSerialNo": "",
    #                     "dtEndDate": "2017/6/29 9:24:59",
    #                     "vcCodeImages": "http://picture.ewemai.com/sq/20170607/qr_3a6aa4994b4cea2b4a9cb7c20bdb7c4f.png",
    #                     "vcNickName": "抱抱0411",
    #                     "dtCreateDate": "2017/6/29 9:14:59"
    #                 }
    #             ]
    #         }
    #     ]
    # }

    # recive_msg_open_api()

    # {"nResult": "1", "vcResult": "成功", "Data": [{}]}

    send_chat_message_api()


    # {"nResult": "1", "vcResult": "成功", "Data": [{}]}

    # receive_memeber_info_api()

    # get_chatroom_list_api()


