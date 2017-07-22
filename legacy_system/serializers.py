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

# 消息类型 2001 文字 2002 图片 2003 语音 2004 视频 2005 链接 2006 名片 2007 动态表情 2013 小程序

msg_type_map = {'2001': 1, '2002': 47, '2003': 34, '2005': 50, '2007': 47}

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
    isLegal = serializers.SerializerMethodField('get_is_legal')

    _db_gemii_choice = None
    _info = None

    def get_sernum(self, obj):
        if self._db_gemii_choice:
            return self._db_gemii_choice
        chatroom_id = str(obj.vcChatRoomSerialNo)
        key = 'ChatRoomModel_db_gemii_choice:{vcChatRoomSerialNo}'.format(vcChatRoomSerialNo=chatroom_id)
        db_gemii_choice = cache.get(key)
        if not db_gemii_choice:
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

            cache.set(key, db_gemii_choice)
            self._db_gemii_choice = db_gemii_choice
        else:
            self._db_gemii_choice = db_gemii_choice
        return self._db_gemii_choice

    def get_content(self, obj):
        if str(obj.nMsgType) == '2005':
            django_log.info('链接消息')
            return '#$#'.join([obj.vcShareTitle, obj.vcShareDesc, obj.vcShareUrl])
        if msg_type_map.get(str(obj.nMsgType), None) is None:
            django_log.info("未识别的信息，类型为 %s" % obj.nMsgType)
            return "未识别的信息"
        return obj.vcContent

    def get_msg_type(self, obj):
        return msg_type_map.get(str(obj.nMsgType), 1)

    def get_app_msg_type(self, obj):
        return 0

    def _get_member_info(self, room_id, user_id, db_gemii_choice):
        if self._info:
            return self._info['item']
        key = 'wechatroommemberinfo_data:{room_id}:{user_id}'.format(room_id=room_id, user_id=user_id)
        data = cache.get(key)
        if not data:
            data = {
                'item': None,
            }
            try:
                data['item'] = WeChatRoomMemberInfoGemii.objects.using(db_gemii_choice).get(U_UserID=user_id, RoomID=room_id)
            except WeChatRoomMemberInfoGemii.DoesNotExist:
                pass
            cache.set(key, data)
        self._info = data
        return self._info['item']

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
        info = self._get_member_info(room_id, u_userid, db_gemii_choice)
        return info.MemberID if info else ""

    def get_nickname(self, obj):
        u_userid = str(obj.vcFromWxUserSerialNo)
        room_id = self.get_room_id(obj)
        db_gemii_choice = self.get_sernum(obj)
        info = self._get_member_info(room_id,u_userid,db_gemii_choice)
        return info.NickName if info else ""

    def get_mermer_icon(self, obj):
        room_id = self.get_room_id(obj)
        u_userid = str(obj.vcFromWxUserSerialNo)
        db_gemii_choice = self.get_sernum(obj)
        info = self._get_member_info(room_id,u_userid,db_gemii_choice)
        return info.member_icon if info else ""


    def get_creat_time(self, obj):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_is_legal(self, obj):
        room_id = self.get_room_id(obj)
        u_userid = str(obj.vcFromWxUserSerialNo)
        db_gemii_choice = self.get_sernum(obj)
        info = self._get_member_info(room_id,u_userid,db_gemii_choice)
        return info.is_legal if info else ""

    class Meta:
        model = ChatMessageModel
        fields = ('Content', 'MsgType', 'AppMsgType', 'UserDisplayName', 'MsgId', 'CreateTime', 'RoomID',
                  'MemberID', 'UserNickName', 'MemberIcon', 'isLegal')
