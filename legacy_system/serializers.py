# coding:utf-8
'''
Created on 2017年6月1日

'''
from rest_framework import serializers
from connector.models import ChatMessageModel, MemberInfo
from connector.utils.mysql_db import MysqlDB
from connector.utils.db_config import DBCONF

import logging

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
    CreateTime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='dtMsgTime')
    RoomID = serializers.SerializerMethodField('get_room_id')
    MemberID = serializers.SerializerMethodField('get_member_id')
    UserNickName = serializers.SerializerMethodField('get_nickname')
    MemberIcon = serializers.SerializerMethodField('get_mermer_icon')

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
        u_roomid = obj.vcChatRoomSerialNo

        mysql = MysqlDB(DBCONF.wechat_gemii_config)
        try:
            room_record = mysql.select('WeChatRoomInfo', where_dict={'U_RoomID': str(u_roomid)})
            roomId = room_record[0]['RoomID']
            # if room_record:
            #     roomId = room_record[0]['RoomID']
            # else:
            #     roomId = ''
            #     django_log.info('未找到发送消息对应的群')
        except:
            return ''
        finally:
            mysql.close()

        return roomId

    def get_member_id(self, obj):
        mysql_gemii = MysqlDB(DBCONF.wechat_gemii_config)
        mysql_bot = MysqlDB(DBCONF.wechat4bot2hye_config)

        try:
            room_id = self.get_room_id(obj)
            # u_userid = mysql_bot.select('UserInfo', where_dict={'U_UserID': str(obj.vcFromWxUserSerialNo)})
            memeber_record = mysql_gemii.select('WeChatRoomMemberInfo',
                                                where_dict={'U_UserID': str(obj.vcFromWxUserSerialNo),
                                                            'RoomID': str(room_id)})
            memeber_id = memeber_record[0]['MemberID']
        except:
            return ''
        finally:
            mysql_bot.close()
            mysql_gemii.close()

        return memeber_id

    def get_nickname(self, obj):
        print obj.vcFromWxUserSerialNo, 'hello'
        mysql_gemii = MysqlDB(DBCONF.wechat_gemii_config)
        try:
            u_userid = mysql_gemii.select('WeChatRoomMemberInfo',
                                          where_dict={'U_UserID': str(obj.vcFromWxUserSerialNo)})
            # user_name = MemberInfo.objects.get(vcSerialNo=str(obj.vcFromWxUserSerialNo))
            user_nickname = u_userid[0]['NickName']
        except:
            return ''
        finally:
            mysql_gemii.close()

        return user_nickname

    def get_mermer_icon(self, obj):
        mysql_gemii = MysqlDB(DBCONF.wechat_gemii_config)
        mysql_bot = MysqlDB(DBCONF.wechat4bot2hye_config)

        try:
            room_id = self.get_room_id(obj)
            # u_userid = mysql_bot.select('UserInfo', where_dict={'U_UserID': str(obj.vcFromWxUserSerialNo)})
            memeber_record = mysql_gemii.select('WeChatRoomMemberInfo',
                                                where_dict={'U_UserID': str(obj.vcFromWxUserSerialNo),
                                                            'RoomID': str(room_id)})

            member_icon = memeber_record[0]['member_icon']
        except:
            return ''
        finally:
            mysql_bot.close()
            mysql_gemii.close()
        return member_icon

    #    def get_default_name(self, obj):
    #        return ''

    class Meta:
        model = ChatMessageModel
        fields = ('Content', 'MsgType', 'AppMsgType', 'UserDisplayName', 'MsgId', 'CreateTime', 'RoomID',
                  'MemberID', 'UserNickName', 'MemberIcon')
