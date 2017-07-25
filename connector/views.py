# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

import random
import string
import time
import json
import datetime
import requests
import logging
import copy

import redis

from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from rest_framework import mixins
from rest_framework import viewsets
from django.core.cache import cache
from rest_framework.generics import GenericAPIView
from decorate import view_exception_handler
from connector import apis
from connector.models import ChatMessageModel, URobotModel, ChatRoomModel, \
    IntoChatRoomMessageModel, IntoChatRoom, DropOutChatRoom, MemberInfo, RoomTask,RobotChatRoom, GemiiRobot,\
    WhileList, RobotBlockedModel
from wechat.models import WeChatRoomInfoGemii, WeChatRoomMemberInfoGemii, WeChatRoomMessageGemii, \
    Monitor, MonitorRoom
from wyeth.models import WeChatRoomMemberInfo, UserInfo, UserStatus, WeChatRoomInfo
from connector.serializers import ChatMessageSerializer, URobotSerializer, \
    ChatRoomSerializer, IntoChatRoomMessageSerializer, IntoChatRoomSerializer, \
    DropOutChatRoomSerializer, MemberInfoSerializer, RobotBlockedSerialize

from connector.forms import KickingForm

from django.db.models import F
from django.conf import settings
from connector.utils import commont_tool
from django.db import transaction

from legacy_system.publish import pub_message
# Create your views here.

django_log = logging.getLogger('django')
message_log = logging.getLogger('message')
member_log = logging.getLogger('member')
sql_log = logging.getLogger('sql')

CODE_STR = string.ascii_letters + string.digits


class Tick(object):
    def _get_cache_key(self, key):
        return 'TICK:{key}'.format(key=key)

    def _get_cache(self, key):
        return cache.get(self._get_cache_key(key))

    def _set_cache(self, key, value):
        cache.set(self._get_cache_key(key), value, timeout=None)

    def get_ayd(self):
        return self._get_cache('ayd')

    def set_ayd(self, value):
        self._set_cache('ayd', value)
    #
    # def get_msj(self):
    #     return self._get_cache('msj')
    #
    # def set_msj(self, value):
    #     self._set_cache('msj', value)

    # def get_wyeth(self):
    #     return self._get_cache('wyeth')
    #
    # def set_wyeth(self, value):
    #     self._set_cache('wyeth', value)

class KickingRedis(object):

    def __init__(self, conf):
        host = conf['host']
        port = conf['port']
        password = conf['password']
        db = conf['db']
        self.type = conf['type']
        self.redis = redis.StrictRedis(host=host, port=port, password=password, db=db)

        self.channel_pub = 'p20170701_'


class KickingSendMsg(object):

    def kicking_send_msg(self, chatroom_record, sernum, u_roomid, u_userid, roomid, monitorname=None):
        vcRobotSerialNo = chatroom_record.vcRobotSerialNo
        content = settings.KICKINGCONTENT
        apis.send_chat_message(vcRobotSerialNo=vcRobotSerialNo, vcChatRoomSerialNo=u_roomid,
                               vcWeixinSerialNo=u_userid, msgContent=content)
        if monitorname is None:
            if sernum == "A":
                try:
                    monitorroom = MonitorRoom.objects.using('gemii').get(RoomID=roomid)
                    monitorid = monitorroom.MonitorID
                    monitor = Monitor.objects.using('gemii').get(id=monitorid)
                    monitorname = monitor.UserName
                except MonitorRoom.DoesNotExist:
                    monitorname = ""
            else:
                try:
                    monitorroom = MonitorRoom.objects.using('gemii_b').get(RoomID=roomid)
                    monitorid = monitorroom.MonitorID
                    monitor = Monitor.objects.using('gemii_b').get(id=monitorid)
                    monitorname = monitor.UserName
                except MonitorRoom.DoesNotExist:
                    monitorname = ""

        robot_msg = {
            "Content": content,
            "MsgType": 1,
            "AppMsgType": 0,
            "UserDisplayName": monitorname,
            "MsgId": ''.join(random.sample(CODE_STR, random.randint(20, 24))),
            "CreateTime": time.strftime('%Y-%m-%d %H:%M:%S'),
            "RoomID": roomid,
            "MemberID": "",
            "UserNickName": monitorname
        }

        if sernum == 'A':
            WeChatRoomMessageGemii.objects.using('gemii').create(**robot_msg)
            redis_a = KickingRedis(settings.REDIS_CONFIG['redis_a'])
            robot_msg['isLegal'] = "1"
            redis_a.redis.publish(redis_a.channel_pub, json.dumps(robot_msg))
        else:
            WeChatRoomMessageGemii.objects.using('gemii_b').create(**robot_msg)
            redis_b = KickingRedis(settings.REDIS_CONFIG['redis_b'])
            robot_msg['isLegal'] = "1"
            redis_b.redis.publish(redis_b.channel_pub, json.dumps(robot_msg))


class UMessageView(GenericAPIView, mixins.CreateModelMixin):
    """
    由创回调数据基类
    """
    def batch_create(self, request, datas=None, *args, **kwargs):
        for data in datas:
            try:
                rsp = apis.receive_member_info(str(data['vcChatRoomSerialNo']))
                django_log.info('room-id:%s' % data['vcChatRoomSerialNo'])
                django_log.info('rsp:%s' % rsp)
            except Exception,e:
                django_log.info(e)
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)

    @view_exception_handler
    def post(self, request, *args, **kwargs):
        datas = json.loads(request.data['strContext'],strict=False)['Data']
        if datas:
            self.batch_create(request, datas=datas, *args, **kwargs)
        return HttpResponse('SUCCESS')

class URobotView(viewsets.ModelViewSet):
    queryset = URobotModel.objects.all()
    serializer_class = URobotSerializer

class ChatRoomView(viewsets.ModelViewSet):
    queryset = ChatRoomModel.objects.all()
    serializer_class = ChatRoomSerializer

    @view_exception_handler
    def create(self, request, *args, **kwargs):
        django_log.info('open_room_success_callback')
        request_data = json.loads(request.data['strContext'], strict=False)['Data']
        for data in request_data:
            u_roomid = data['vcChatRoomSerialNo']
            try:
                room_record = ChatRoomModel.objects.get(vcChatRoomSerialNo=u_roomid)
                room_record.vcBase64Name = data['vcBase64Name']
                room_record.vcWxUserSerialNo = data['vcWxUserSerialNo']
                room_record.vcName = data['vcName']
                room_record.vcRobotSerialNo = data['vcRobotSerialNo']
                room_record.vcApplyCodeSerialNo = data['vcApplyCodeSerialNo']
                room_record.save()
            except:
                serializer = self.get_serializer(data=data)
                if serializer.is_valid():
                    self.perform_create(serializer)
            rsp = commont_tool.rece_msg(u_roomid)
            django_log.info('rece_msg_rsp %s' % str(rsp))
        return HttpResponse('SUCCESS')

class ChatMessageListView(viewsets.ModelViewSet):
    queryset = ChatMessageModel.objects.all()
    serializer_class = ChatMessageSerializer

    @view_exception_handler
    def create(self, request, *args, **kwargs):
        request_data = json.loads(request.data['strContext'], strict=False)['Data']
        for data in request_data:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)

        return HttpResponse('SUCCESS')

class IntoChatRoomMessageCreateView(GenericAPIView, mixins.CreateModelMixin):
    queryset = IntoChatRoomMessageModel.objects.all()
    serializer_class = IntoChatRoomMessageSerializer
    def create(self, request, *args, **kwargs):
        django_log.info('robot_into_collback')
        request_data = json.loads(request.data['strContext'], strict=False)['Data']
        for data in request_data:
            state = '0'
            try:
                rsp = commont_tool.open_room(data['vcSerialNo'])
            except Exception,e:
                rsp = ''
            if rsp:
                rsp = json.loads(rsp)
                if int(rsp['nResult']) == 1:
                    state = '1'
            data['state'] = state

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
        return HttpResponse('SUCCESS')

    @view_exception_handler
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class IntoChatRoomCreateView(GenericAPIView, mixins.CreateModelMixin):
    """
    成员入群信息
    """
    queryset = IntoChatRoom.objects.all()
    serializer_class = IntoChatRoomSerializer

    def batch_create(self, request, datas=None, *args, **kwargs):
        member_log.info('成员入群回调')
        for data in datas:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
        self.handle_member_room(datas)

    def handle_member_room(self, members):
        """
        参数 说明
           vcChatRoomSerialNo 群编号
            vcWxUserSerialNo 用户编号
            vcFatherWxUserSerialNo 邀请人用户编号
            vcNickName 用户昵称
            vcBase64NickName Base64编码后的用户昵称
            vcHeadImages 用户头像
            nJoinChatRoomType 入群方式 10扫码 11拉入 12未知

        :param members:
        :return:
        """
        member_log.info('开始插入roommember数据（%s）' % len(members))
        for member in members:
            u_roomid = member['vcChatRoomSerialNo']
            u_userid = member['vcWxUserSerialNo']

            if str(u_userid) == "7A2868EE3CA4A0FDE990AC1A319FE369":
                member_log.info('踢特定用户 7A2868EE3CA4A0FDE990AC1A319FE369')
                response = apis.chatroom_kicking(vcChatRoomSerialNo=u_roomid, vcWxUserSerialNo=u_userid)
                member_log.info('response %s' % str(response))
                continue

            try:
                chatroom_record = ChatRoomModel.objects.get(vcChatRoomSerialNo=u_roomid)
                serNum = str(chatroom_record.serNum)
            except ChatRoomModel.DoesNotExist:
                serNum = 'B'
                chatroom_record = ""

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
                room_record = WeChatRoomInfoGemii.objects.using(db_gemii_choice).get(U_RoomID=u_roomid)
            except WeChatRoomInfoGemii.DoesNotExist:
                room_record = ""

            if not room_record:
                member_log.info('未匹配u_userid(%s)入的群WeChatRoomInfo[%s]数据' % (
                str(member['vcWxUserSerialNo']), str(member['vcChatRoomSerialNo'])))
                continue
            else:
                try:
                    user_record = UserInfo.objects.get(U_UserID=u_userid, MatchGroup=room_record.RoomID)
                except UserInfo.DoesNotExist:
                    user_record = ""

                roommerber_data = {
                    'RoomID': room_record.RoomID,
                    'NickName': member['vcNickName'],
                    'U_UserID': member['vcWxUserSerialNo'],
                    'member_icon': member['vcHeadImages'],
                    'DisplayName': member['vcNickName'],
                }

                room_member = WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).filter(RoomID=room_record.RoomID, U_UserID=u_userid)
                if room_member.exists():
                    member_log.info('roommember数据已存在（RoomID：%s,U_UserID:%s）' % (
                    str(room_record.RoomID), str(u_userid)))
                    continue

                if user_record:
                    roommerber_data['open_id'] = user_record.Openid
                    roommerber_data['UserID'] = user_record.id

                if db_gemii_choice == 'gemii_b' and not user_record:
                    member_log.info('私拉用户')
                    roommerber_data['is_legal'] = '0'

                gemii_data = copy.copy(roommerber_data)

                gemii_data['MemberID'] = u_userid
                gemii_data['enter_group_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).create(**gemii_data)
                WeChatRoomMemberInfo.objects.using(db_wyeth_choice).create(**roommerber_data)
                member_log.info('成功插入成员数据--u_userid(%s)入的群WeChatRoomInfo[%s]' % (str(u_userid), str(u_roomid)))
                WeChatRoomInfoGemii.objects.using(db_gemii_choice).filter(U_RoomID=u_roomid).update(
                    currentCount=F('currentCount') + 1)
                WeChatRoomInfo.objects.using(db_wyeth_choice).filter(U_RoomID=u_roomid).update(
                    currentCount=F('currentCount') + 1)

                # 机器人拉人不踢
                vcFatherWxUserSerialNo = member["vcFatherWxUserSerialNo"]
                if not vcFatherWxUserSerialNo:
                    member_log.info('no vcFatherWxUserSerialNo')
                    continue
                member_log.info('vcFatherWxUserSerialNo %s' % str(vcFatherWxUserSerialNo))
                fatherrobot = GemiiRobot.objects.filter(vcRobotSerialNo=vcFatherWxUserSerialNo)
                if fatherrobot.exists():
                    vcName = fatherrobot.first().vcName
                    member_log.info('机器人 %s 拉人入群 %s' % (vcName.encode('utf-8'), vcFatherWxUserSerialNo.encode('utf-8')))
                    continue

                tickCfg = Tick()
                ayd_task = tickCfg.get_ayd()
                # msj_task = tickCfg.get_msj()
                # wyeth_task = tickCfg.get_wyeth()

                if not user_record:
                    if (ayd_task and str(room_record.owner) == 'aiyingdao'):
                        # (msj_task and str(room_record.owner) == 'meisujiaer'):
                        # (wyeth_task and str(room_record.owner) == 'wyeth'):
                        # member_log.info('私拉踢人的项目--> 爱婴岛: %s, 美素佳儿: %s, 惠氏: %s' % (str(ayd_task), str(msj_task), str(wyeth_task)))
                        member_log.info('私拉踢人的项目--> 爱婴岛: %s' % (str(ayd_task)))
                        if chatroom_record:
                            roomid = room_record.RoomID
                            kick = KickingSendMsg()
                            kick.kicking_send_msg(chatroom_record, serNum, u_roomid, u_userid, roomid)
                            time.sleep(2)

                        response = apis.chatroom_kicking(vcChatRoomSerialNo=u_roomid, vcWxUserSerialNo=u_userid)
                        data = json.loads(response)
                        if str(data['nResult']) == "1":
                            member_log.info('私拉踢人已打开，%s 用户已被移出群 %s' % (str(u_userid), str(u_roomid)))
                        else:
                            member_log.info('私拉踢人已打开，由创返回码 %s' % str(response))

    @view_exception_handler
    def post(self, request, *args, **kwargs):
        datas = json.loads(request.data['strContext'], strict=False)['Data']
        if datas:
            self.batch_create(request, datas=datas, *args, **kwargs)
        return HttpResponse('SUCCESS')


class DropOutChatRoomCreateView(GenericAPIView, mixins.CreateModelMixin):
    """
    成员退群信息
    vcChatRoomSerialNo 群编号
    vcWxUserSerialNo 用户编号
    dtCreateDate 退群时间
    """
    queryset = DropOutChatRoom.objects.all()
    serializer_class = DropOutChatRoomSerializer

    def batch_create(self, request, datas=None, *args, **kwargs):
        member_log.info('成员退群回调')
        member_log.info('处理退群成员数量 %s' %(str(len(datas))))

        count = 0
        for data in datas:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)

            u_roomid = data['vcChatRoomSerialNo']
            u_userid= data['vcWxUserSerialNo']
            try:
                chatroom_record = ChatRoomModel.objects.get(vcChatRoomSerialNo=u_roomid)
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
                room_record = WeChatRoomInfoGemii.objects.using(db_gemii_choice).get(U_RoomID=u_roomid)
            except WeChatRoomInfoGemii.DoesNotExist:
                room_record = ''

            if not room_record:
                member_log.info('未匹配u_userid(%s)入的群WeChatRoomInfo[%s]数据' % (
                str(data['vcWxUserSerialNo']), str(data['vcChatRoomSerialNo'])))
                continue
            else:
                roomid = room_record.RoomID
                WeChatRoomMemberInfo.objects.using(db_wyeth_choice).filter(RoomID=roomid, U_UserID=u_userid).delete()
                WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).filter(RoomID=roomid, U_UserID=u_userid).delete()
                self.delete_member_cache(roomid, u_userid)
            count += 1
            WeChatRoomInfoGemii.objects.using(db_gemii_choice).filter(U_RoomID=u_roomid).update(currentCount=F('currentCount') - 1)
            WeChatRoomInfo.objects.using(db_wyeth_choice).filter(U_RoomID=u_roomid).update(currentCount=F('currentCount') - 1)
        member_log.info('成功处理退群成员（%s）个' % count)

    def delete_member_cache(self, roomid, u_userid):
        key = 'wechatroommemberinfo_data:{room_id}:{user_id}'.format(room_id=roomid, user_id=u_userid)
        return cache.delete(key)

    @view_exception_handler
    def post(self, request, *args, **kwargs):
        datas = json.loads(request.data['strContext'], strict=False)['Data']
        if datas:
            self.batch_create(request, datas=datas, *args, **kwargs)
        return HttpResponse('SUCCESS')


class MemberInfoCreateView(GenericAPIView, mixins.CreateModelMixin):
    queryset = MemberInfo.objects.all()
    serializer_class = MemberInfoSerializer

    def batch_create(self, request, members=None, chatroom_id=None):
        if not members or not chatroom_id:
            django_log.info(u'没有群（%s）成员：' % (chatroom_id))
            return HttpResponse('SUCCESS')
        members = members[0]['ChatRoomUserData']

        try:
            chatroom = ChatRoomModel.objects.get(vcChatRoomSerialNo=chatroom_id)
        except ChatRoomModel.DoesNotExist:
            chatroom = ''

        for member in members:
            serializer = self.get_serializer(data=member)
            if serializer.is_valid():
                self.perform_create(serializer)
                if chatroom:
                    chatroom.member.add(serializer.instance)
            else:
                instance = MemberInfo.objects.filter(vcSerialNo=member['vcSerialNo'])
                if member['dtCreateDate']:
                    member['dtCreateDate'] = commont_tool.time_strf(member['dtCreateDate'])
                if member['dtLastMsgDate']:
                    member['dtLastMsgDate'] = commont_tool.time_strf(member['dtLastMsgDate'])
                else:
                    member.pop('dtLastMsgDate')
                instance.update(**member)
                if chatroom:
                    if not chatroom.member.filter(vcSerialNo=member['vcSerialNo']).exists():
                        print 'enter inset chatroom'
                        chatroom.member.add(instance.first())

        member_log.info('更新群成员数据（%s）' % (str(chatroom_id)))
        self.handle_member_room(members, chatroom_id)
        return HttpResponse('SUCCESS')

    @view_exception_handler
    def post(self, request, *args, **kwargs):
        data = json.loads(request.data['strContext'], strict=False)
        members = data['Data']
        chatroom_id = data['vcChatRoomSerialNo']
        return self.batch_create(request, members=members, chatroom_id=chatroom_id)

    @transaction.atomic()
    def handle_member_room(self, members, chatroom_id):
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
            self.insert_room_member_data(member, roominfo_raw, userinfo_raw, db_gemii_choice, db_wyeth_choice)
            count += 1
        member_log.info('更新U_RoomID：%s的(%s)个成员信息成功' % (str(chatroom_id), count))
        WeChatRoomInfoGemii.objects.using(db_gemii_choice).filter(U_RoomID=chatroom_id).update(currentCount=count)
        WeChatRoomInfo.objects.using(db_wyeth_choice).filter(U_RoomID=chatroom_id).update(currentCount=count)

    def insert_room_member_data(self, member, roominfo_raw, userinfo_raw, db_gemii_choice, db_wyeth_choice):
        roommember_data = {
            'RoomID': roominfo_raw.RoomID,
            'NickName': member['vcNickName'],
            'U_UserID': member['vcSerialNo'],
            'member_icon': member['vcHeadImages'],
            'DisplayName': member['vcNickName'],
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

        WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).create(**gemii_data)
        WeChatRoomMemberInfo.objects.using(db_wyeth_choice).create(**roommember_data)


class GetUrobotQucode(View):
    def get_urobot_qrcode(self, request):
        response = {'code': 0, 'msg': '成功'}
        try:
            task_id = request.POST['task_id']
            chat_room_id = request.POST['chat_room_id']
            open_id = request.POST['open_id']
            group_id = request.POST['group_id']
            group_name = request.POST['group_name']
        except Exception:
            response = {'code': 1, 'msg': '表单参数错误'}
            return response

        params = {
            "task_id": task_id,
            "label_id": '',
            "open_id": open_id,
            "group_id": group_id,
            "group_name": group_name,
            "chat_room_id": chat_room_id,
        }

        u_response = json.loads(apis.get_robot_qrcode(**params))

        if 'data' in u_response and u_response['data'] and u_response['data']['task_account']:

            data = {
                'qr_url': u_response['data']['task_account']['qr_code'],
                'verify_code': u_response['data']['task_account']['verify_code']
            }

            response['data'] = data
        else:
            django_log.info('获取二维码失败：%s' % request.POST)
            django_log.info('u_response：%s' % u_response)
            response = {'code': 1, 'msg': '获取二维码失败'}
        return response

    @view_exception_handler
    def post(self, request):
        response = self.get_urobot_qrcode(request)
        return HttpResponse(json.dumps(response), content_type="application/json")


class UnotityCallback(View):
    def unotity_callback(self, request):
        """
        :param request:
            open_id 用户微信openid
            room_id  群ID(由创)
            room_name 群名称
            group_id  群id(景栗)
            user_id   用户唯一标识符(微信id或其他)
            verify_code  验证码
            user_nickname 用户昵称
            user_head_img 用户头像
            result_code 结果码
            description 结果描述(可选)
        :return:
        """
        response = {'code': 0, 'msg': '成功'}
        try:
            open_id = request.POST['open_id']
            room_id = request.POST['room_id']
            room_name = request.POST['room_name']
            user_head_img = request.POST['user_head_img']
            user_id = request.POST['user_id']
            verify_code = request.POST['verify_code']
            user_nickname = request.POST['user_nickname']
        except Exception:
            response = {'code': 1, 'msg': '表单参数错误'}
            return response

        try:
            chatroom_record = ChatRoomModel.objects.get(vcChatRoomSerialNo=room_id)
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
            member_log.info('选择b库')

        try:
            room_record = WeChatRoomInfo.objects.using(db_wyeth_choice).get(U_RoomID=room_id)
        except WeChatRoomInfo.DoesNotExist:
            member_log.info('未匹配到WeChatRoomInfo[%s]数据' % (str(room_id)))
            return None

        userinfo_records = UserInfo.objects.using(db_wyeth_choice).filter(Openid=open_id, MatchGroup=room_record.RoomID)

        if userinfo_records.exists():
            userinfo_records.update(U_UserID=user_id, UserName=user_nickname)
            member_log.info('update userinfo')
            userinfo_record = userinfo_records.first()

            now = datetime.datetime.now()
            user_status_parm = {
                'PhoneCode': verify_code,
                'UserID': user_id,
                'FriendStatus': '已确认好友',
                'EnterGroupStatus': '已入群',
                'userInfo': userinfo_record,
                'FriendTime': now,
                'ConfirmStatus': now,
                'GroupTime': now,
                'MatchStatus': '群匹配成功',
                'MatchGroup': userinfo_record.MatchGroup,
                'UserName': user_nickname,
                'Type': 'offers',
            }

            # 2017/7/11-2017/7/18 data loss
            UserStatus.objects.using(db_wyeth_choice).create(**user_status_parm)
            member_log.info('成功插入UserStatus数据：%s' % user_status_parm)
            self.handle_member_enter_room(room_id, room_name, user_id, user_nickname, userinfo_record, user_head_img, db_wyeth_choice, db_gemii_choice)
        else:
            response = {'code': 1, 'msg': '未找到openid关联的用户'}

        return response

    def handle_member_enter_room(self, u_roomid, room_name, u_user_id, user_nickname, userinfo_raw, user_head_img, db_wyeth_choice, db_gemii_choice):
        try:
            room_record = WeChatRoomInfoGemii.objects.using(db_gemii_choice).get(U_RoomID=u_roomid)
        except WeChatRoomInfo.DoesNotExist:
            room_record = ""

        if room_record and userinfo_raw:
            roommerber_data = {
                'RoomID': room_record.RoomID,
                'NickName': user_nickname,
                'member_icon': user_head_img,
                'open_id': userinfo_raw.Openid,
                'UserID': userinfo_raw.id,
                'U_UserID': u_user_id,
                'DisplayName': user_nickname,
            }

            gemii_data = copy.copy(roommerber_data)
            gemii_data['enter_group_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            gemii_data['MemberID'] = u_user_id

            room_member = WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).filter(RoomID=room_record.RoomID,
                                                                                          U_UserID=u_user_id)
            if room_member.exists():
                member_log.info('roommember数据已存在（RoomID：%s,U_UserID:%s）' % (
                    str(room_record.RoomID), str(u_user_id)))
                return

            WeChatRoomMemberInfo.objects.using(db_wyeth_choice).create(**roommerber_data)
            WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).create(**gemii_data)

            WeChatRoomInfoGemii.objects.using(db_gemii_choice).filter(U_RoomID=u_roomid).update(currentCount=F('currentCount') + 1)
            WeChatRoomInfo.objects.using(db_wyeth_choice).filter(U_RoomID=u_roomid).update(currentCount=F('currentCount') + 1)

    @view_exception_handler
    def post(self, request):
        response = self.unotity_callback(request)
        return HttpResponse(json.dumps(response), content_type="application/json")

# write 2017/6/27 by kefei

class ChatRoomKickingView(View):
    """踢人处理"""
    @view_exception_handler
    def get(self, request, *args, **kwargs):
        vcChatRoomSerialNo = request.GET['u_roomId']
        vcWxUserSerialNo = request.GET['u_userId']
        RoomID = request.GET.get('roomId', '')
        monitorName = request.GET.get('monitorName', '')
        member_log.info('java调用踢人接口, 群 %s 用户 %s' % (str(vcChatRoomSerialNo), str(vcWxUserSerialNo)))

        try:
            chatroom_record = ChatRoomModel.objects.get(vcChatRoomSerialNo=vcChatRoomSerialNo)
            serNum = str(chatroom_record.serNum)
        except ChatRoomModel.DoesNotExist:
            serNum = 'B'
            chatroom_record = ""
            member_log.info('未获取到群信息')

        if chatroom_record:
            member_log.info('踢人群信息: 班长--> %s, 群编号: %s' % (str(monitorName), str(RoomID)))
            if RoomID and monitorName:
                kick = KickingSendMsg()
                kick.kicking_send_msg(chatroom_record, serNum, vcChatRoomSerialNo, vcWxUserSerialNo, RoomID, monitorname=monitorName)
                time.sleep(2)

        response = apis.chatroom_kicking(vcRelationSerialNo="",
                                         vcChatRoomSerialNo=vcChatRoomSerialNo,
                                         vcWxUserSerialNo=vcWxUserSerialNo,
                                         vcComment="test")

        kicking_data = json.loads(response)
        if str(kicking_data['nResult']) == "1":
            member_log.info('踢人接口调用成功')
        else:
            member_log.info('由创踢人返回码错误 %s' % str(response))
        return HttpResponse(response, content_type="application/json")


class CreateRoomTaskView(View):
    """接受建群任务进行建群处理"""
    def create_room_task(self, request, *args, **kwargs):
        # 解析请求参数
        serNum = request.POST.get('serNum', False)
        theme = request.POST.get('theme', False)
        introduce = request.POST.get('introduce', False)
        limit_member_count = request.POST.get('limit_member_count', False)
        count = request.POST.get('count', False)
        # 参数传递不全时返回
        if not (theme and introduce and limit_member_count and count and serNum):
            msg = {'code': 1, 'msg': "请传递完整的参数"}
            return msg

        # 创建建群任务
        create_task_response = apis.create_chatroom_task(theme, introduce, limit_member_count)
        # 解析建群请求
        create_task_data = json.loads(create_task_response)
        if create_task_data['code'] != 0:
            return create_task_data

        task_data = create_task_data['data']
        # 获取建群任务返回的数据
        task_id = task_data['task_id']
        theme_image = task_data['theme_image']
        creator = task_data['creator']
        create_time = task_data['create_time']
        # 激活建群任务
        apis.active_chatroom_task(task_id, theme, theme_image,
                                  count, creator, create_time)

        # 创建群
        createroom_response = apis.create_chatroom(task_id)
        createroom_data = json.loads(createroom_response)
        if createroom_data['code'] != 0:
            return createroom_data

        qr_code = createroom_data['data']['qr_code']
        verify_code = createroom_data['data']['verify_code']
        # 返回格式
        response = {
            'code': 0,
            'msg': "",
            "data": {
                'task_id': task_id,
                'qr_code': qr_code,
                'verify_code': verify_code
            }
        }

        django_log.info('创群返回参数 %s' % str(response))

        # TODO 获取java传过来的库编号，写入RoomTask中
        roomtask = RoomTask(serNum=serNum, task_id=task_id)
        roomtask.save()

        django_log.info('存入库编号: %s , task_id: %s ' % (str(serNum), str(task_id)))

        return response
    @view_exception_handler
    def post(self, request, *args, **kwargs):
        response = self.create_room_task(request, *args, **kwargs)
        return HttpResponse(json.dumps(response, ensure_ascii=False),
                            content_type="application/json")


class CreateRoomCallbackView(View):
    """建群信息回调并返回信息给java"""
    @view_exception_handler
    def post(self, request, *args, **kwargs):

        task_id = request.POST.get('task_id', False)
        if not task_id:
            msg = {'code': 1, 'msg': "请传递完整的参数"}
            return HttpResponse(json.dumps(msg, ensure_ascii=False),
                                content_type="application/json")
        get_chatrooms = apis.group_chatroom_id(task_id)

        room_data = json.loads(get_chatrooms)['data']

        room_info_list = []
        # 获取群信息
        for room in room_data:
            chat_room_id = room['chat_room_id']
            chat_room_name = room['chat_room_name']
            create_time = room['create_time']

            room_info_list.append({
                'uRoomId': chat_room_id,
                'roomName': chat_room_name,
                'createTime': create_time
            })

        # 调用java接口发送群信息
        params = {
            'taskId': task_id,
            'data': room_info_list
        }

        # TODO 写入数据到群信息表中
        # 根据task_id获取库编号
        try:
            serNum_record = RoomTask.objects.get(task_id=task_id)
            serNum = serNum_record.serNum

            # 写入数据到群信息表中
            for room_info in room_info_list:
                vcChatRoomSerialNo = room_info['uRoomId']
                vcName = room_info['roomName']

                room_record = ChatRoomModel.objects.filter(vcChatRoomSerialNo=vcChatRoomSerialNo)
                if room_record.exists():
                    continue

                chatroom = ChatRoomModel(vcChatRoomSerialNo=vcChatRoomSerialNo,
                                         vcName=vcName, serNum=serNum, vcBase64Name=vcName)
                chatroom.save()
                django_log.info('插入数据至群信息')
        except RoomTask.DoesNotExist:
            django_log.info('未找到任务编号')

        response = requests.post(settings.CALLBACK_JAVA, data={"params": json.dumps(params)})

        return HttpResponse('SUCCESS.')


class ModifyRoomNameView(View):
    """由java调用修改群名称"""
    def modify_room_name(self, request):
        django_log.info('进入修改群名接口回调')
        task_id = request.POST.get('task_id', False)
        chat_room_id = request.POST.get('chat_room_id', False)
        chat_room_name = request.POST.get('chat_room_name', False)
        create_time = request.POST.get('create_time', False)

        if not (task_id and chat_room_id and chat_room_name and create_time):
            msg = {'code': 1, 'msg': "请传递完整的参数"}
            return msg
        # 调由创接口修改群名
        response = apis.modify_chatroom_info(
            task_id, chat_room_id, chat_room_name, create_time)

        django_log.info('修改群名回调 %s' % str(response))

        modify_roomname_data = json.loads(response)
        if str(modify_roomname_data['code']) == "0":

            vcName = modify_roomname_data['data']['chat_room_name']

            # TODO 写入数据到群信息表中
            try:
                chatroom_record = ChatRoomModel.objects.get(vcChatRoomSerialNo=chat_room_id)
                chatroom_record.vcName = vcName
                chatroom_record.save()
                django_log.info('修改群信息表中的群名')
            except ChatRoomModel.DoesNotExist:
                django_log.info('未找到任务编号')
        else:
            django_log.info('modify chatroom failed, chat_room_id --> %s' % str(chat_room_id))

        return modify_roomname_data

    @view_exception_handler
    def post(self, request, *args, **kwargs):
        response  = self.modify_room_name(request)
        return HttpResponse(json.dumps(response), content_type="application/json")

class OpenKickingView(View):
    def get(self, request):
        kicking_form = KickingForm()
        return render(request, 'kicking_task.html', {'kicking_form': kicking_form})

    def post(self, request):
        kicking_form = KickingForm(request.POST)
        if kicking_form.is_valid():
            member_log.info('私拉踢人接口调用')

            ayd = request.POST.get('ayd_task', 'close')
            # msj = request.POST.get('msj_task', 'close')
            # wyeth = request.POST.get('wyeth_task', 'close')

            # member_log.info('爱婴岛状态: %s, 美素佳儿状态: %s, 惠氏状态: %s' % (str(ayd), str(msj), str(wyeth)))
            member_log.info('爱婴岛状态: %s' % (str(ayd)))

            tickCfg = Tick()

            if ayd == 'open':
                tickCfg.set_ayd(True)
            elif ayd == 'close':
                tickCfg.set_ayd(False)

            # if msj == 'open':
            #     tickCfg.set_msj(True)
            # elif msj == 'close':
            #     tickCfg.set_msj(False)

            # if wyeth == 'open':
            #     tickCfg.set_wyeth(True)
            # elif wyeth == 'close':
            #     tickCfg.set_wyeth(False)

            return HttpResponseRedirect('/connector/showtask/')
        return render(request, 'kicking_task.html', {'kicking_form': kicking_form})


class ShowKickingView(View):
    def get(self, request):
        tickCfg = Tick()

        ayd = tickCfg.get_ayd()
        # msj = tickCfg.get_msj()
        # wyeth = tickCfg.get_wyeth()

        if ayd == True:
            ayd_task = "私拉踢人已开通"
        elif ayd == False:
            ayd_task = "私拉踢人未开通"
        else:
            ayd_task = "请先设置爱婴岛私拉开关"

        # if msj == True:
        #     msj_task = "私拉踢人已开通"
        # elif msj == False:
        #     msj_task = "私拉踢人未开通"
        #
        # if wyeth == True:
        #     wyeth_task = "私拉踢人已开通"
        # elif wyeth == False:
        #     wyeth_task = "私拉踢人未开通"

        # return render(request, 'show_task.html', {'ayd': ayd_task, 'msj': msj_task, 'wyeth': wyeth_task})
        return render(request, 'show_task.html', {'ayd': ayd_task})

class RebotRoomView(View):
    def batch_create(self,request):
        data = json.loads(request.POST['strContext'], strict=False)
        vcrobotserialno = data['vcRobotSerialNo']
        nodatas = data.get('NoData', [])
        datas = data.get('Data', [])
        create_list = []

        for nodata in nodatas:
            robot_chatroom = RobotChatRoom.objects.filter(vcRobotSerialNo=vcrobotserialno,
                                                          vcChatRoomSerialNo=nodata['vcChatRoomSerialNo'])
            if robot_chatroom.exists():
                robot_chatroom.update(state='0')
            else:
                create_list.append(RobotChatRoom(vcRobotSerialNo=vcrobotserialno, vcChatRoomSerialNo=nodata['vcChatRoomSerialNo'], state='0'))

        for data in datas:
            robot_chatroom = RobotChatRoom.objects.filter(vcRobotSerialNo=vcrobotserialno,
                                                          vcChatRoomSerialNo=data['vcChatRoomSerialNo'])
            if robot_chatroom.exists():
                robot_chatroom.update(state='1')
            else:
                create_list.append(RobotChatRoom(vcRobotSerialNo=vcrobotserialno, vcChatRoomSerialNo=data['vcChatRoomSerialNo'], state='1'))
        if create_list:
            RobotChatRoom.objects.bulk_create(create_list)
        return HttpResponse('SUCCESS')

    @view_exception_handler
    def post(self, request):
        return self.batch_create(request)

class RobotBlockedView(GenericAPIView, mixins.CreateModelMixin):
    queryset = RobotBlockedModel.objects.all()
    serializer_class = RobotBlockedSerialize

    def batch_create(self, request):
        data = json.loads(request.POST['strContext'], strict=False)
        robotinfo = data['Data'][0]['RobotInfo']
        for robot in robotinfo:
            serializer = self.get_serializer(data=robot)
            if serializer.is_valid():
                self.perform_create(serializer)
        return HttpResponse('SUCCESS')

    @view_exception_handler
    def post(self, request):
        return self.batch_create(request)

class Qrcode(View):
    """
        {
      “prefix”:"",
      “suffix”:"",
      "dirname":"",
      "infos":[
               {"filename":"","params":""},
               {"filename":"","params":""},
               {"filename":"","params":""},
              ]
    }
    """

    def post(self, request):
        return self.qrcode_make(request)

    def qrcode_make(self, request):
        import qrcode
        import os
        import shutil
        from connector.utils import short_url
        try:
            data = request.body
            data = json.loads(data)
            prefix = data['prefix']
            suffix = data['suffix']
            dirname = data['dirname']
            infos = data['infos']
        except:
            rsp = {
                "resultCode": "-1",
                "desc": "缺少必要的参数",
            }
            sql_log.info('accep java data')
            sql_log.info(request.body)
            return HttpResponse(json.dumps(rsp), content_type="application/json")

        dir_path = '/var/helper/qrcords/%s' % dirname

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            shutil.rmtree(dir_path)

        for info in infos:
            params = info['params']
            filename = info['filename']
            url = '%s%s%s' % (prefix, params, suffix)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            url = short_url.get_short_url_from_sina(url) or url
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image()
            filename = '%s%s' % (filename, '.png')
            fn = os.path.join(dir_path, filename)
            img.save(fn)

        rsp = {
                "resultCode": "100",
                "desc": "二维码生成成功",
                "resultContent": {"filepath": "/var/helper/qrcords/%s" % dirname}
                }

        return HttpResponse(json.dumps(rsp), content_type="application/json")
