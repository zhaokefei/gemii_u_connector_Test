# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

import time
import json
import datetime
import requests
import logging
from django.views.generic import View

from django.http.response import HttpResponse
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView

from connector import apis
from connector.models import ChatMessageModel, URobotModel, ChatRoomModel, \
    IntoChatRoomMessageModel, IntoChatRoom, DropOutChatRoom, MemberInfo, RoomTask
from wechat.models import WeChatRoomInfoGemii, WeChatRoomMemberInfoGemii
from wyeth.models import WeChatRoomMemberInfo, UserInfo, UserStatus, WeChatRoomInfo
from connector.serializers import ChatMessageSerializer, URobotSerializer, \
    ChatRoomSerializer, IntoChatRoomMessageSerializer, IntoChatRoomSerializer, \
    DropOutChatRoomSerializer, MemberInfoSerializer

from django.conf import settings

from legacy_system.publish import pub_message,intochatroom, rece_msg
# Create your views here.

django_log = logging.getLogger('django')
message_log = logging.getLogger('message')
member_log = logging.getLogger('member')

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

    def post(self, request, *args, **kwargs):
        datas = json.loads(request.data['strContext'])['Data']
        if datas:
            self.batch_create(request, datas=datas, *args, **kwargs)
        return HttpResponse('SUCCESS')

class URobotView(viewsets.ModelViewSet):
    queryset = URobotModel.objects.all()
    serializer_class = URobotSerializer

class ChatRoomView(viewsets.ModelViewSet):
    queryset = ChatRoomModel.objects.all()
    serializer_class = ChatRoomSerializer

    def create(self, request, *args, **kwargs):
        request_data = json.loads(request.data['strContext'])['Data']
        for data in request_data:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
        return HttpResponse('SUCCESS')

class ChatMessageListView(viewsets.ModelViewSet):
    queryset = ChatMessageModel.objects.all()
    serializer_class = ChatMessageSerializer

    def create(self, request, *args, **kwargs):
        request_data = json.loads(request.data['strContext'])['Data']
        for data in request_data:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
        return HttpResponse('SUCCESS')

class IntoChatRoomMessageCreateView(GenericAPIView, mixins.CreateModelMixin):
    queryset = IntoChatRoomMessageModel.objects.all()
    serializer_class = IntoChatRoomMessageSerializer

    def create(self, request, *args, **kwargs):
        request_data = json.loads(request.data['strContext'])['Data']
        for data in request_data:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
        return HttpResponse('SUCCESS')
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
            try:
                chatroom_record = ChatRoomModel.objects.get(vcChatRoomSerialNo=u_roomid)
                serNum = chatroom_record.serNum
            except ChatRoomModel.DoesNotExist:
                serNum = 'B'

            if serNum == 'A':
                db_gemii_choice = 'gemii'
                db_wyeth_choice = 'wyeth'
            # TODo elif serNum=='B'
            else:
                db_gemii_choice = 'gemii_b'
                db_wyeth_choice = 'wyeth_b'

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

                gemii_data = roommerber_data

                gemii_data['MemberID'] = u_userid
                gemii_data['enter_group_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).create(**gemii_data)
                WeChatRoomMemberInfo.objects.using(db_wyeth_choice).create(**roommerber_data)
                member_log.info('成功插入成员数据--u_userid(%s)入的群WeChatRoomInfo[%s]' % (str(u_userid), str(u_roomid)))


    def post(self, request, *args, **kwargs):
        datas = json.loads(request.data['strContext'])['Data']
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
                serNum = chatroom_record.serNum
            except ChatRoomModel.DoesNotExist:
                serNum = 'B'

            if serNum == 'A':
                db_gemii_choice = 'gemii'
                db_wyeth_choice = 'wyeth'
            # TODo elif serNum=='B'
            else:
                db_gemii_choice = 'gemii_b'
                db_wyeth_choice = 'wyeth_b'

            try:
                room_record = WeChatRoomInfoGemii.objects.using(db_gemii_choice).get(U_RoomID=u_roomid)
            except WeChatRoomInfoGemii.DoesNotExist:
                room_record = ''

            if not room_record:
                member_log.info('未匹配u_userid(%s)入的群WeChatRoomInfo[%s]数据' % (
                str(data['vcWxUserSerialNo']), str(data['vcChatRoomSerialNo'])))
                continue
            else:
                WeChatRoomMemberInfo.objects.using(db_wyeth_choice).filter(RoomID=room_record.RoomID, U_UserID=u_userid).delete()
                WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).filter(RoomID=room_record.RoomID, U_UserID=u_userid).delete()
            count += 1

        member_log.info('成功处理退群成员（%s）个' % count)

    def post(self, request, *args, **kwargs):
        datas = json.loads(request.data['strContext'])['Data']
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

        # tmp = 'room_id:%s,count:%s' % (chatroom_id,len(members))
        #
        # commont_tool.save_json('members_count1.txt',tmp,'/var/log/django/data/')

        for member in members:
            serializer = self.get_serializer(data=member)
            if serializer.is_valid():
                self.perform_create(serializer)
                # chatroom = ChatRoomModel.objects.get(vcChatRoomSerialNo=chatroom_id)
                # chatroom.member.add(serializer.instance)
        django_log.info('更新群成员数据（%s）' % (str(chatroom_id)))
        self.handle_member_room(members, chatroom_id)
        return HttpResponse('SUCCESS')

    def post(self, request, *args, **kwargs):
        #
        import re
        regex = re.compile(r'\\(?![/u"])')
        fixed = regex.sub(r"\\\\", request.data['strContext'])
        try:
            data = json.loads(fixed)
        except ValueError:
            member_data = fixed.replace('\\', '\\\\')
            try:
                data = json.loads(member_data)
            except ValueError:
                # try:
                data = json.loads(member_data.replace('\r', '\\r').replace('\n', '\\n'))
                # except:
                #
                #     commont_tool.save_json('fault.json', request.data['strContext'], '/var/log/django/data/')
        # data = request.data['strContext']
        # try:
        #     data = json.loads(data)
        # except Exception,e:
        #     commont_tool.save_json('member.json',data,'/var/log/django/data/member/')

        members = data['Data']
        chatroom_id = data['vcChatRoomSerialNo']
        return self.batch_create(request, members=members, chatroom_id=chatroom_id)

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
            serNum = chatroom_record.serNum
        except ChatRoomModel.DoesNotExist:
            serNum = 'B'

        if serNum == 'A':
            db_gemii_choice = 'gemii'
            db_wyeth_choice = 'wyeth'
        # TODo elif serNum=='B'
        else:
            db_gemii_choice = 'gemii_b'
            db_wyeth_choice = 'wyeth_b'

        try:
            roominfo_raw = WeChatRoomInfoGemii.objects.using(db_gemii_choice).get(U_RoomID=chatroom_id)
        except WeChatRoomInfoGemii.DoesNotExist:
            django_log.info('未匹配到WeChatRoomInfo[%s]数据' % (str(chatroom_id)))
            return None
        django_log.info('开始更新U_RoomID：%s的成员信息' % (str(chatroom_id)))
        WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).filter(RoomID=roominfo_raw.RoomID).delete()
        WeChatRoomMemberInfo.objects.using(db_wyeth_choice).filter(RoomID=roominfo_raw.RoomID).delete()

        count = 0
        for member in members:
            # try:
            #     userinfo_raw = UserInfo.objects.using(db_wyeth_choice).filter(U_UserID=member['vcSerialNo'])
            # except UserInfo.DoesNotExist:
            #     django_log.info('未匹配到UserInfo [%s]数据' % (member['vcSerialNo']))
            #     userinfo_raw = ''
            userinfo_raws = UserInfo.objects.using(db_wyeth_choice).filter(U_UserID=member['vcSerialNo'])
            if userinfo_raws:
                userinfo_raw = userinfo_raws.first()
            else:
                userinfo_raw = ''
            self.insert_room_member_data(member, roominfo_raw, userinfo_raw, db_gemii_choice, db_wyeth_choice)
            count += 1
        django_log.info('更新U_RoomID：%s的(%s)个成员信息成功' % (str(chatroom_id), count))

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
            roommember_data['UserID'] = userinfo_raw.id

        gemii_data = roommember_data

        gemii_data['MemberID'] = member['vcSerialNo']

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
            serNum = chatroom_record.serNum
        except ChatRoomModel.DoesNotExist:
            serNum = 'B'

        if serNum == 'A':
            db_gemii_choice = 'gemii'
            db_wyeth_choice = 'wyeth'
        # TODo elif serNum=='B'
        else:
            db_gemii_choice = 'gemii_b'
            db_wyeth_choice = 'wyeth_b'

        try:
            room_record = WeChatRoomInfo.objects.using(db_wyeth_choice).get(U_RoomID=room_id)
        except WeChatRoomMemberInfo.DoesNotExist:
            django_log.info('未匹配到WeChatRoomInfo[%s]数据' % (str(room_id)))
            return None

        userinfo_records = UserInfo.objects.using(db_wyeth_choice).filter(Openid=open_id, MatchGroup=room_record.RoomID)

        if userinfo_records.exists():
            userinfo_records.update(U_UserID=user_id, UserName=user_nickname)
            userinfo_record = userinfo_records.first()

            now = datetime.datetime.now()
            user_status_parm = {
                'PhoneCode': verify_code,
                'UserID': user_id,
                'FriendStatus': '已确认好友',
                'EnterGroupStatus': '已入群',
                'FKUserInfoID': userinfo_record.id,
                'FriendTime': now,
                'ConfirmStatus': now,
                'GroupTime': now,
                'MatchStatus': '群匹配成功',
                'MatchGroup': userinfo_record.MatchGroup,
                'UserName': user_nickname,
                'Type': 'offers',
            }

            UserStatus.objects.create(**user_status_parm)
            django_log.info('成功插入UserStatus数据：%s' % user_status_parm)
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

            gemii_data = roommerber_data
            gemii_data['enter_group_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            gemii_data['MemberID'] = u_user_id

            WeChatRoomMemberInfo.objects.using(db_wyeth_choice).create(**roommerber_data)
            WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).create(**gemii_data)

    def post(self, request):
        response = self.unotity_callback(request)
        return HttpResponse(json.dumps(response), content_type="application/json")

# write 2017/6/27 by kefei

class ChatRoomKickingView(View):
    """踢人处理"""
    def get(self, request, *args, **kwargs):
        vcChatRoomSerialNo = request.GET['u_roomId']
        vcWxUserSerialNo = request.GET['u_userId']
        response = apis.chatroom_kicking(vcRelationSerialNo="",
                                         vcChatRoomSerialNo=vcChatRoomSerialNo,
                                         vcWxUserSerialNo=vcWxUserSerialNo,
                                         vcComment="test")
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

        # TODO 获取java传过来的库编号，写入RoomTask中
        roomtask = RoomTask(serNum=serNum, task_id=task_id)
        roomtask.save()

        return response

    def post(self, request, *args, **kwargs):
        response = self.create_room_task(request, *args, **kwargs)
        return HttpResponse(json.dumps(response, ensure_ascii=False),
                            content_type="application/json")


class CreateRoomCallbackView(View):
    """建群信息回调并返回信息给java"""
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

        response = requests.post(settings.CALLBACK_JAVA, data={"params": json.dumps(params)})

        # TODO 写入数据到群信息表中
        # 根据task_id获取库编号
        try:
            serNum_record = RoomTask.objects.get(task_id=task_id)
            serNum = serNum_record.serNum

            # 写入数据到群信息表中
            for room_info in room_info_list:
                vcChatRoomSerialNo = room_info['uRoomId']
                vcName = room_info['roomName']

                chatroom = ChatRoomModel(vcChatRoomSerialNo=vcChatRoomSerialNo,
                                         vcName=vcName, serNum=serNum)
                chatroom.save()
        except RoomTask.DoesNotExist:
            django_log.info('未找到任务编号')

        return HttpResponse('SUCCESS.')


class ModifyRoomNameView(View):
    """由java调用修改群名称"""
    def modify_room_name(self, request):
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

        modify_roomname_data = json.loads(response)

        return modify_roomname_data

    def post(self, request, *args, **kwargs):
        response  = self.modify_room_name(request)
        return HttpResponse(json.dumps(response), content_type="application/json")

