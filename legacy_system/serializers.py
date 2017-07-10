# coding:utf-8
'''
Created on 2017年6月1日

'''

import datetime
import logging

from rest_framework import serializers
from connector.models import ChatMessageModel
from django.core.cache import cache
from connector.models import ChatRoomModel
from wechat.models import WeChatRoomInfoGemii, WeChatRoomMemberInfoGemii

# old system
# {
#     "Content": "生仔好愁",
#     "MsgType": 1,
#     "AppMsgType": 0,
#     "UserDisplayName": "拉风+2017.4.16剖帅哥",
#     "MsgId": "6978638240095723167",
#     "CreateTime": "2017-05-24 14:54:02",
#     "RoomID": "DS13142",
#     "MemberID": "225958b4a38f588fcb321392537f72bf",
#     "UserNickName": "🦄"
# }
django_log = logging.getLogger('django')

msg_type_map = {'2001': 1, '2002': 47, '2005': 49, '2003': 34}

class LegacyChatRoomMessageSerializer(serializers.ModelSerializer):
    Content = serializers.SerializerMethodField('get_content')
    MsgType = serializers.SerializerMethodField('get_msg_type')
    AppMsgType = serializers.SerializerMethodField('get_app_msg_type')
    UserDisplayName = serializers.SerializerMethodField('get_nickname')
    MsgId = serializers.CharField(source='vcSerialNo')
    CreateTime = serializers.SerializerMethodField('get_creat_time')
    RoomID = serializers.SerializerMethodField('get_room_id')
    MemberID = serializers.SerializerMethodField('get_member_id')
    UserNickName = serializers.SerializerMethodField('get_nickname')
    MemberIcon = serializers.SerializerMethodField('get_mermer_icon')

    def get_sernum(self, obj):
        chatroom_id = str(obj.vcChatRoomSerialNo)
        try:
            chatroom_record = ChatRoomModel.objects.get(vcChatRoomSerialNo=chatroom_id)
            serNum = chatroom_record.serNum
        except ChatRoomModel.DoesNotExist:
            serNum = 'B'

        if serNum == 'A':
            db_gemii_choice = 'gemii'
        # TODo elif serNum=='B'
        else:
            db_gemii_choice = 'gemii_b'

        return db_gemii_choice

    def get_content(self, obj):
        if msg_type_map.get(str(obj.nMsgType), None) is None:
            django_log.info("未识别的信息，类型为 %s" % obj.nMsgType)
            return "未识别的信息"
        return obj.vcContent

    def get_msg_type(self, obj):
        return msg_type_map.get(str(obj.nMsgType), 1)

    def get_app_msg_type(self, obj):
        return 0

    def get_room_id(self, obj):
        db_gemii_choice = self.get_sernum(obj)
        u_roomid = str(obj.vcChatRoomSerialNo)
        key = 'wechatroominfo_roomid:{u_roomid}'.format(u_roomid=u_roomid)
        room_id = cache.get(key)
        if not room_id:
            try:
                room_record = WeChatRoomInfoGemii.objects.using(db_gemii_choice).get(U_RoomID=u_roomid)
                room_id = room_record.RoomID
            except WeChatRoomInfoGemii.DoesNotExist:
                room_id = ""
            cache.set(key, room_id)

        return room_id

    def get_member_id(self, obj):
        u_userid = str(obj.vcFromWxUserSerialNo)
        db_gemii_choice = self.get_sernum(obj)
        room_id = self.get_room_id(obj)
        key = 'wechatroommemberinfo_memberid:{room_id}:{u_userid}'.format(room_id=room_id, u_userid=u_userid)
        member_id = cache.get(key)
        if not member_id:
            try:
                member_record = WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).get(U_UserID=u_userid, RoomID=room_id)
                member_id = member_record.MemberID
            except WeChatRoomMemberInfoGemii.DoesNotExist:
                member_id = ""

            cache.set(key, member_id)

        return member_id

    def get_nickname(self, obj):
        u_userid = str(obj.vcFromWxUserSerialNo)
        room_id = self.get_room_id(obj)
        db_gemii_choice = self.get_sernum(obj)
        key = 'wechatroommemberinfo_username:{u_userid}'.format(u_userid=u_userid)
        user_nickname = cache.get(key)
        if not user_nickname:
            try:
                nickname_record = WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).get(U_UserID=u_userid, RoomID=room_id)
                user_nickname = nickname_record.NickName
            except WeChatRoomMemberInfoGemii.DoesNotExist:
                user_nickname = ""

            cache.set(key, user_nickname)

        return user_nickname

    def get_mermer_icon(self, obj):
        room_id = self.get_room_id(obj)
        u_userid = str(obj.vcFromWxUserSerialNo)
        db_gemii_choice = self.get_sernum(obj)
        # cache
        key = 'wechatroommemberinfo_membericon:{room_id}:{u_userid}'.format(room_id=room_id, u_userid=u_userid)
        member_icon = cache.get(key)
        if not member_icon:
            try:
                member_icon_record = WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).get(U_UserID=u_userid, RoomID=room_id)
                member_icon = member_icon_record.member_icon
            except WeChatRoomMemberInfoGemii.DoesNotExist:
                member_icon = ""

            cache.set(key, member_icon)

        return member_icon

    def get_creat_time(self, obj):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    class Meta:
        model = ChatMessageModel
        fields = ('Content', 'MsgType', 'AppMsgType', 'UserDisplayName', 'MsgId', 'CreateTime', 'RoomID',
                  'MemberID', 'UserNickName', 'MemberIcon')
