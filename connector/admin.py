# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from connector.models import ChatMessageModel,URobotModel,ChatRoomModel,\
IntoChatRoomMessageModel,IntoChatRoom, DropOutChatRoom, MemberInfo,RobotChatRoom,GemiiRobot,WhileList

# Register your models here.
class ChatMessageModelAdmin(admin.ModelAdmin):
    list_display = ('vcSerialNo', 'vcChatRoomSerialNo', 'vcFromWxUserSerialNo',
                    'dtMsgTime', 'vcContent')
    search_fields = ('vcSerialNo', 'vcChatRoomSerialNo', 'vcFromWxUserSerialNo')

class URobotModelAdmin(admin.ModelAdmin):
    list_filter = ('nStatus',)
    list_display = ('vcSerialNo', 'vcNickName', 'nStatus', 'nChatRoomCount', 'vcCodeImages',)
    search_fields = ('vcSerialNo', 'vcNickName',)
    
class ChatRoomModelAdmin(admin.ModelAdmin):
    list_display = ('vcChatRoomSerialNo', 'vcName', 'vcRobotSerialNo')
    search_fields = ('vcChatRoomSerialNo', 'vcName', 'vcRobotSerialNo')

class IntoChatRoomMessageModelAdmin(admin.ModelAdmin):
    list_display = ('vcSerialNo', 'vcRobotSerialNo', 'vcName', 'dtCreateDate')
    search_fields = ('vcSerialNo', 'vcRobotSerialNo', 'vcName',)

    
class IntoChatRoomAdmin(admin.ModelAdmin):
    list_display = ('vcChatRoomSerialNo', 'vcWxUserSerialNo', 'vcNickName', 'message_create_time')
    search_fields = ('vcChatRoomSerialNo', 'vcWxUserSerialNo', 'vcNickName',)

class DropOutChatRoomAdmin(admin.ModelAdmin):
    list_display = ('vcChatRoomSerialNo', 'vcWxUserSerialNo', 'dtCreateDate')
    search_fields = ('vcChatRoomSerialNo', 'vcWxUserSerialNo',)

class MemberInfoAdmin(admin.ModelAdmin):
    list_display = ('vcSerialNo', 'vcNickName', 'dtCreateDate')
    search_fields = ('vcSerialNo', 'vcNickName',)

class RobotChatRoomAdmin(admin.ModelAdmin):
    list_filter = ('state',)
    list_display = ('vcRobotSerialNo', 'vcChatRoomSerialNo', 'state')
    search_fields = ('vcRobotSerialNo', 'vcChatRoomSerialNo',)

class GemiiRobotAdmin(admin.ModelAdmin):
    list_display = ('vcRobotSerialNo', 'vcName', 'qrcode')
    search_fields = ('vcRobotSerialNo', 'vcName')

class WhileListAdmin(admin.ModelAdmin):
    list_filter = ('flag',)
    list_display = ('vcChatRoomSerialNo', 'vcWxUserSerialNo')
    search_fields = ('vcChatRoomSerialNo', 'vcWxUserSerialNo')

admin.site.register(ChatMessageModel, ChatMessageModelAdmin)
admin.site.register(URobotModel, URobotModelAdmin)
admin.site.register(ChatRoomModel, ChatRoomModelAdmin)
admin.site.register(IntoChatRoomMessageModel, IntoChatRoomMessageModelAdmin)
admin.site.register(IntoChatRoom, IntoChatRoomAdmin)
admin.site.register(DropOutChatRoom, DropOutChatRoomAdmin)
admin.site.register(MemberInfo, MemberInfoAdmin)
admin.site.register(RobotChatRoom, RobotChatRoomAdmin)
admin.site.register(GemiiRobot, GemiiRobotAdmin)
admin.site.register(WhileList, WhileListAdmin)
