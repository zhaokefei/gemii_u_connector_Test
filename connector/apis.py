# coding:utf-8
'''
Created on 2017年6月20日

@author: hepeng
'''
import hashlib
import json
import urllib
import requests
from request import URequest, URequestVer2
from django.conf import settings
import logging



No = settings.NO
Sec = settings.SEC


def md5_args(arg_src):
    m = hashlib.md5()
    m.update(arg_src)
    return m.hexdigest()

# 把 data格式数据 转换成 url 并且加密
def gen_data(strContext):
    strSign = md5_args(json.dumps(strContext)+Sec)
    data = {'strContext': json.dumps(strContext), 'strSign': strSign}
    data = urllib.urlencode(data)
    return data

# 机器人 在群内发送消息
def send_chat_message(vcChatRoomSerialNo='',
                 vcRobotSerialNo='',
                 nIsHit='1',
                 vcWeixinSerialNo='',
                 nMsgType='2001',
                 msgContent='',
                 vcTitle='',
                 vcDesc='',
                 vcHref='',
                 nVoiceTime='0'):
    api = 'Merchant.asmx/MerchantSendMessages'
    params = {
        'MerchantNo': No,
        'vcRelaSerialNo': '',
        'vcChatRoomSerialNo': str(vcChatRoomSerialNo),
        'vcRobotSerialNo': str(vcRobotSerialNo),
        'nIsHit': str(nIsHit),
        'vcWeixinSerialNo': str(vcWeixinSerialNo),
        'Data':[
            {
                'nMsgType': str(nMsgType),
                'msgContent': msgContent.encode('utf-8'),
                'vcTitle': vcTitle.encode('utf-8'),
                'vcDesc': vcDesc.encode('utf-8'),
                'vcHref': vcHref.encode('utf-8'),
                'nVoiceTime': str(nVoiceTime)}
            ]
        }
    # 传入data格式数据
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 更新 群成员 获取群成员
def receive_member_info(vcChatRoomSerialNo=''):
    api = 'Merchant.asmx/ChatRoomUserInfo'
    params = {
        'MerchantNo': No,
        'vcChatRoomSerialNo': vcChatRoomSerialNo
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 批量 开群 手动激活 就调用这个。
def open_chatroom(vcSerialNoList=''):
    api = 'Merchant.asmx/PullRobotInChatRoomOpenChatRoom'
    params = {
        'MerchantNo': No,
        'vcSerialNoList': vcSerialNoList
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 开启 群内 实时消息
def open_get_message(vcChatRoomSerialNo=''):
    api = 'Merchant.asmx/ChatRoomOpenGetMessages'
    params = {
        'MerchantNo': No,
        'vcChatRoomSerialNo': vcChatRoomSerialNo
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 查看 机器人 开通的群
def get_chatroom_list(vcRobotSerialNo=''):
    api = 'Merchant.asmx/ChatRoomList'
    params = {
        'MerchantNo': No,
        'vcRobotSerialNo': vcRobotSerialNo
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 获取 机器人列表
def get_robot_list():
    api = 'Merchant.asmx/RobotList'
    params = {
        'MerchantNo': No
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 群内@人发送消息
def chatroom_sendmsg(vcRelaSerialNo, vcChatRoomSerialNo, vcRobotSerialNo,
                     vcWeixinSerialNo, nIsHit=1, Data=None):
    """

    @brief 群内@人发送消息
    :param vcRelaSerialNo:
    :param vcChatRoomSerialNo: RoomIDs
    :param vcRobotSerialNo: Uin
    :param vcWeixinSerialNo: memberIds
    :param nIsHit: 0 @所有人 ； 1 @单个人, atAll
    :param Data:
        Data = [{
        "nMsgType": nMsgType, MsgType
        "msgContent": msgContent,  Content
        "vcTitle": vcTitle,
        "vcDesc": vcDesc,
        "nVoiceTime": nVoiceTime,
        "vcHref": vcHref
    }, {}, {}]
    :return:
    """
    api = "Merchant.asmx/MerchantSendMessages"
    if Data is None:
        Data = []

    params = {
        "MerchantNo": No,
        "vcRelaSerialNo": vcRelaSerialNo,
        "vcChatRoomSerialNo": vcChatRoomSerialNo,
        "vcRobotSerialNo": vcRobotSerialNo,
        "nIsHit": nIsHit,
        "vcWeixinSerialNo": vcWeixinSerialNo,
        "Data": Data
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 群主群内踢人
def chatroom_kicking(vcRelationSerialNo="",
                     vcChatRoomSerialNo="",
                     vcWxUserSerialNo="",
                     vcComment="test"):
    """
    @brief 群主群内踢人
    :param vcRelationSerialNo:
    :param vcChatRoomSerialNo:
    :param vcWxUserSerialNo:
    :param vcComment:
    :return:
    """
    api = 'Merchant.asmx/ChatRoomKicking'
    params = {
        "MerchantNo": No,
        'Data': [
            {
                'vcRelationSerialNo': vcRelationSerialNo,
                'vcChatRoomSerialNo': vcChatRoomSerialNo,
                'vcWxUserSerialNo': vcWxUserSerialNo,
                'vcComment': vcComment
            }
        ]
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 创建开群任务
def create_chatroom_task(theme, introduce, limit_member_count, bot_code):
    """
    @brief 创建开群任务
    :param theme: 群名[5-20]字符
    :param introduce: 群简介[10-200]字符
    :param limit_member_count: 群成员数量上限[30, 450]人
    :return:
    """
    api = "v1/task/create"
    params = {
        "theme": theme,
        "introduce": introduce,
        "price": 0.0,
        "limit_member_count": limit_member_count,
        "bot_code": bot_code,
        "type": 12
    }
    u_request = URequestVer2()
    u_request.api = api
    u_request.data = json.dumps(params)
    response = u_request.request()
    return response

# 激活开群任务
def active_chatroom_task(task_id, theme, theme_image,
                         pay_count, creator, create_time):
    """
    @brief 激活开群任务
    :param task_id: 任务id(由创建开群任务提供)
    :param theme: 群名(由创建开群任务提供)
    :param theme_image: 群图像(由创建开群任务提供)
    :param pay_count: 开群数量
    :param creator: 创建人OpenID
    :param create_time: 创建时间(由创建开群任务提供)
    :return:
    """
    api = "v1/task/virtual-pay"
    params = {
        "task_id": task_id,
        "theme": theme,
        "theme_image": theme_image,
        "pay_count": pay_count,
        "is_paid": True,
        "creator": creator,
        "create_time": create_time,
        "type": 12,
        "status": 11
    }
    u_request = URequestVer2(method=requests.put)
    u_request.api = api
    u_request.data = json.dumps(params)
    response = u_request.request()
    return response


def create_chatroom(task_id):
    """
    @brief 创建群
    :param task_id: 任务id
    :return:
    """
    api = "v1/task/admin/%s" % task_id
    params = {}

    u_request = URequestVer2(method=requests.get)
    u_request.api = api
    u_request.data = json.dumps(params)
    response = u_request.request()
    return response

# 修改群信息 - 返回 java 接口
def modify_chatroom_info(task_id, chat_room_id,
                         chat_room_name, create_time, qr_code='', exist_creator='', notice=""):
    """
    @brief 修改群信息（修改群名）
    :param task_id:
    :param chat_room_id:
    :param chat_room_name:
    :param create_time:
    :param notice:
    :param qr_code:
    :param exist_creator:
    :return:
    """
    api = "v1/group/chat-room"
    params = {
        "task_id": task_id,
        "chat_room_id": chat_room_id,
        "chat_room_name": chat_room_name,
        "create_time": create_time,
        "notice": notice,
        "qr_code": qr_code,
        "exist_creator": exist_creator
    }
    u_request = URequestVer2(method=requests.put)
    u_request.api = api
    u_request.data = json.dumps(params)
    response = u_request.request()
    return response

# 通过任务ID获取微信群列表
def group_chatroom_id(task_id):
    """
    @brief 通过任务ID获取微信群列表
    :param task_id:
    :param keyword:
    :return:
    """
    api = "v1/group/chat-rooms/{0}".format(task_id)
    u_request = URequestVer2(method=requests.get)
    u_request.api = api
    response = u_request.request()
    return response

# 获取机器人二维码
def get_robot_qrcode(task_id, label_id, open_id,
                     group_id, group_name, chat_room_id):
    """
    @brief 获取机器人二维码
    :param task_id:
    :param label_id:
    :param open_id:
    :param group_id:
    :param group_name:
    :param chat_room_id:
    :return:
    """
    api = "v1/group/task-account"
    params = {
        "task_id": task_id,
        "label_id": label_id,
        "open_id": open_id,
        "group_id": group_id,
        "group_name": group_name,
        "chat_room_id": chat_room_id,
        "code": "code",
        "instance_id": '123456'
    }
    u_request = URequestVer2(method=requests.post)
    u_request.api = api
    u_request.data = json.dumps(params)
    response = u_request.request()
    return response


# 转移群主
def change_chatroom_admin(task_id='', chat_room_id='', admin_wxid=''):
    api = "v1/group/admin-transfer"
    data = []
    params = {
        "task_id": task_id,
        "chat_room_id": chat_room_id,
        "admin_wxid": admin_wxid
        # "admin_exist": True,
        # "transfer_status": 5
    }
    u_request = URequestVer2(method=requests.post)
    u_request.api = api
    data.append(params)
    u_request.data = json.dumps(data)
    response = u_request.request()
    return response


def get_qrcode():
    """获取消息处理二维码"""
    api = "Merchant.asmx/ApplyCodeList"
    params = {
        "MerchantNo": No,
        "vcRobotSerialNo": "",
        "nType": 10,
        "vcChatRoomSerialNo": "",
        "nCodeCount": 1,
        "nAddMinute": 10,
        "nIsNotify": 0,
        "vcNotifyContent": ""
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

def recive_msg_open(room_id):
    """开启消息接收"""
    api = "Merchant.asmx/ChatRoomOpenGetMessages"
    params = {
        "MerchantNo": No,
        "vcChatRoomSerialNo": room_id
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 注销 开通的群
def room_over(vcChatRoomSerialNo=''):
    api = 'Merchant.asmx/ChatRoomOver'
    params = {
        'MerchantNo': No,
        'vcChatRoomSerialNo': vcChatRoomSerialNo,
        'vcComment': 'test'
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 转让 群主
def chatroomadminchange(vcChatRoomSerialNo='', vcWxUserSerialNo=''):
    api = 'Merchant.asmx/ChatRoomAdminChange'
    params = {
        'MerchantNo': No,
        'vcChatRoomSerialNo': vcChatRoomSerialNo,
        'vcWxUserSerialNo': vcWxUserSerialNo
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 修改群信息
def chatroominfomodify(vcChatRoomSerialNo='', vcName='', vcNotice='', nInviteSwitch='1'):
    """
    修改群信息
    :param vcChatRoomSerialNo:
    :param vcName:
    :param vcNotice:
    :param nInviteSwitch: 需给定默认值,不可传空
    :return:
    """
    api = 'Merchant.asmx/ChatRoomInfoModify'
    params = {
        'MerchantNo': No,
        'vcChatRoomSerialNo': vcChatRoomSerialNo,
        'vcName': vcName,
        'vcNotice': vcNotice,
        'nInviteSwitch': str(nInviteSwitch)
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

# 查询 群信息。
def checkchatroomstatus(vcChatRoomSerialNo=''):
    api = 'Merchant.asmx/ChatRoomStatus'
    params = {
        'MerchantNo': No,
        'vcChatRoomSerialNo': vcChatRoomSerialNo,
    }
    data = gen_data(params)
    u_request = URequest()
    u_request.api = api
    u_request.data = data
    response = u_request.request()
    return response

