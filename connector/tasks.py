#!/usr/bin/python
# -*- coding: utf-8 -*-
import StringIO
import json
import logging
import time

import copy

import xlwt
from celery.task import task
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.core import signals

from connector import apis
from connector.models import RobotChatRoom, ChatRoomModel, WhileList, URobotModel, SendEmailMemberModel
from connector.serializers import MemberInfoSerializer
from connector.utils import commont_tool
from wechat.models import WeChatRoomMemberInfoGemii, WeChatRoomInfoGemii
from wyeth.models import WeChatRoomMemberInfo, UserInfo, WeChatRoomInfo

celery_log = logging.getLogger('celery')
member_log = logging.getLogger('member')


@task
def handle_robotchatroom(vcrobotserialno, datas, nodatas):

    from django.db import connection
    with connection.cursor() as cursor:
        ar_nodatas = ','.join([x['vcChatRoomSerialNo'] for x in nodatas])
        if ar_nodatas:
            cursor.callproc("sync_robotchatroom", (vcrobotserialno, ar_nodatas, "0"))
        ar_datas = ','.join([x['vcChatRoomSerialNo'] for x in datas])
        if ar_datas:
            cursor.callproc("sync_robotchatroom", (vcrobotserialno, ar_datas, "1"))


@task
def handle_member_room(members, chatroom_id, chatroom):
    """
    参数	说明
        vcChatRoomSerialNo	群编号
        vcSerialNo	用户编号
        vcNickName	用户昵称
        vcBase64NickName	Base64编码后的用户昵称
        vcHeadImages	用户头像
        nJoinChatRoomType	入群方式 10扫码 11拉入 12未知
        vcFatherWxUserSerialNo	邀请人用户编号
        nMsgCount	当天发言总数
        dtLastMsgDate	当天最后发言时间
        dtCreateDate	入群时间

    :param members:
    :return:
    """
    if chatroom:
        chatroom.member.clear()

    for member in members:
        serializer = MemberInfoSerializer(data=member)
        if serializer.is_valid():
            instance = serializer.create(validated_data=serializer.data)
            if chatroom:
                chatroom.member.add(instance)
        else:
            member_log.info(serializer.errors)

    member_log.info('需要更新的群成员数据为（%s）' % (str(len(members))))
    member_log.info('更新群成员数据（%s）' % (str(chatroom_id)))

    try:
        chatroom_record = ChatRoomModel.objects.get(vcChatRoomSerialNo=chatroom_id)
        serNum = str(chatroom_record.serNum)
    except ChatRoomModel.DoesNotExist:
        serNum = 'B'

    if serNum == 'A':
        db_gemii_choice = 'gemii'
        db_wyeth_choice = 'wyeth'
        member_log.info('选择A库')
    # TODo elif serNum=='B'
    else:
        db_gemii_choice = 'gemii_b'
        db_wyeth_choice = 'wyeth_b'
        member_log.info('选择B库')
    try:
        roominfo_raw = WeChatRoomInfoGemii.objects.using(db_gemii_choice).get(U_RoomID=chatroom_id)
    except WeChatRoomInfoGemii.DoesNotExist:
        member_log.info('未匹配到WeChatRoomInfo[%s]数据' % (str(chatroom_id)))
        return None
    member_log.info('开始更新U_RoomID：%s的成员信息' % (str(chatroom_id)))
    WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).filter(RoomID=roominfo_raw.RoomID).delete()
    WeChatRoomMemberInfo.objects.using(db_wyeth_choice).filter(RoomID=roominfo_raw.RoomID).delete()

    count = 0
    for member in members:
        userinfo_raws = UserInfo.objects.using(db_wyeth_choice).filter(U_UserID=member['vcSerialNo'],MatchGroup=roominfo_raw.RoomID)
        if userinfo_raws:
            userinfo_raw = userinfo_raws.first()
        else:
            userinfo_raw = ''
        insert_room_member_data(member, roominfo_raw, userinfo_raw, db_gemii_choice, db_wyeth_choice)
        count += 1
    member_log.info('更新U_RoomID：%s的(%s)个成员信息成功' % (str(chatroom_id), count))
    WeChatRoomInfoGemii.objects.using(db_gemii_choice).filter(U_RoomID=chatroom_id).update(currentCount=count)
    WeChatRoomInfo.objects.using(db_wyeth_choice).filter(U_RoomID=chatroom_id).update(currentCount=count)

@transaction.atomic()
def insert_room_member_data(member, roominfo_raw, userinfo_raw, db_gemii_choice, db_wyeth_choice):
    origin_name = commont_tool.decode_base64(member['vcBase64NickName']).decode('utf-8')
    nickname = commont_tool.emoji_to_unicode(origin_name)
    roommember_data = {
        'RoomID': roominfo_raw.RoomID,
        'NickName': nickname,
        'U_UserID': member['vcSerialNo'],
        'member_icon': member['vcHeadImages'],
        'DisplayName': nickname,
    }

    if userinfo_raw:
        roommember_data['open_id'] = userinfo_raw.Openid
        roommember_data['UserID'] = str(userinfo_raw.id)

    if db_gemii_choice == 'gemii_b' and not userinfo_raw:
        roommember_data['is_legal'] = '0'

    whilelist = WhileList.objects.filter(vcChatRoomSerialNo=roominfo_raw.U_RoomID,
                                         vcWxUserSerialNo=member['vcSerialNo'], flag='1')
    if whilelist.exists():
        roommember_data['is_legal'] = '2'

    gemii_data = copy.copy(roommember_data)

    gemii_data['MemberID'] = member['vcSerialNo']
    gemii_data['enter_group_time'] = commont_tool.time_strf(member['dtCreateDate'])
    try:
        WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).create(**gemii_data)
        WeChatRoomMemberInfo.objects.using(db_wyeth_choice).create(**roommember_data)
    except Exception, e:
        member_log.info('出现重复的数据 %s' % str(e.message))

# 机器人 被封 发送邮件。
@task
def send_email_robot_blocked(robotid, blockedtime):
    member_log.info('start send message')
    chatroom_record = ChatRoomModel.objects.filter(vcRobotSerialNo=robotid)
    robot_record = URobotModel.objects.get(vcSerialNo=robotid)

    # 创建 stringIO 准备写入数据
    f = StringIO.StringIO()
    # 创建一个 excel
    file = xlwt.Workbook()
    write_table = file.add_sheet(u'机器人被封')
    header = [u'机器人编号', u'机器人名称', u'群编号', u'群名称', u'群主编号', u'群主', u'项目', u'机器人被封时间']
    for i, value in enumerate(header):
        write_table.write(0, i, value)

    for i, chatroom in enumerate(chatroom_record, start=1):
        roomname = chatroom.vcName
        u_roomid = chatroom.vcChatRoomSerialNo
        adminid = chatroom.vcWxUserSerialNo
        serNum = chatroom.serNum
        robotname = robot_record.vcNickName

        # 分库
        if serNum == "A":
            db_gemii_choice = 'gemii'
        else:
            db_gemii_choice = 'gemii_b'

        # 获取项目
        room_record = WeChatRoomInfoGemii.objects.using(db_gemii_choice).filter(U_RoomID=u_roomid)
        if room_record.exists():
            roomid = room_record.first().RoomID
            owner = room_record.first().owner
            if not owner:
                owner = 'wyeth'
        else:
            roomid = u''
            owner = u''

        # 获取群主
        member_record = WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).filter(U_UserID=adminid, RoomID=roomid)
        if member_record.exists():
            adminname = member_record.first().NickName
        else:
            adminname = ''

        write_table.write(i, 0, robotid)
        write_table.write(i, 1, robotname)
        write_table.write(i, 2, roomid)
        write_table.write(i, 3, roomname)
        write_table.write(i, 4, adminid)
        write_table.write(i, 5, adminname)
        write_table.write(i, 6, owner)
        write_table.write(i, 7, str(blockedtime))

    file.save(f)

    # 获取发送邮件的用户邮箱
    email_addresses = []
    send_members = SendEmailMemberModel.objects.filter(send_type='rb')
    for mem in send_members:
        email = mem.Email
        email_addresses.append(email)

    # 整合邮件发送
    email = EmailMessage(
        u'机器人被封反馈',
        settings.EMAIL_BODY,
        settings.EMAIL_FROM,
        email_addresses
    )

    email.attach(u"{}_robot_blocked.xls".format(datetime.now().strftime("%Y-%m-%d")), f.getvalue(), 'application/octet-stream')

    return send_email(email)

def send_email(email, release=3, **kwargs):
    try:
        member_log.info('开始发送邮件')
        response = email.send()
        member_log.info('send email response %s' % str(response))
    except Exception, e:
        member_log.info('error %s' % str(e.message))
        if release > 0:
            member_log.info('重试发送邮件，剩余发送次数%s' % str(release))
            return send_email(email, release-1, **kwargs)
        else:
            member_log.info('发送邮件失败')
            return False

    return response