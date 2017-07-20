# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.
class URobotModel(models.Model):
    # 由创定义属性
    vcSerialNo = models.CharField(max_length=50, unique=True, verbose_name=u'助手编号')
    nChatRoomCount = models.CharField(max_length=5, verbose_name=u'入群数')
    vcNickName = models.CharField(max_length=100, verbose_name=u'助手昵称')
    vcBase64NickName = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'助手base64昵称')
    vcHeadImages = models.CharField(max_length=1000, null=True, blank=True, verbose_name=u'助手头像')
    vcCodeImages = models.CharField(max_length=1000, null=True, blank=True, verbose_name=u'助手二维码')
    nStatus = models.CharField(max_length=10, null=True, blank=True, verbose_name=u'助手状态')
    # 自定义属性
    status = models.BooleanField(default=True, verbose_name=u'是否可用')
    
    class Meta:
        db_table = 'robot_info'
        verbose_name_plural = verbose_name = u'助手信息'

class MemberInfo(models.Model):
    """
    群成员信息表
    """
    vcSerialNo = models.CharField(max_length=50, unique=True, verbose_name=u'用户编号')
    vcNickName = models.CharField(max_length=100, verbose_name=u'用户昵称')
    vcBase64NickName = models.CharField(max_length=100, verbose_name=u'Base64编码后的用户昵称')
    vcHeadImages = models.CharField(max_length=1000, verbose_name=u'用户头像')
    nJoinChatRoomType = models.CharField(max_length=5, verbose_name=u'入群方式')
    vcFatherWxUserSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'用户父级编号(邀请人编号)')
    nMsgCount = models.CharField(max_length=10, verbose_name=u'当天发言总数')
    dtLastMsgDate = models.DateTimeField(null=True, blank=True, verbose_name=u'当天最后发言时间')
    dtCreateDate = models.DateTimeField(null=True, blank=True, verbose_name=u'入群时间')
    
    class Meta:
        db_table = 'member_info'
        verbose_name_plural = verbose_name = u'群成员信息'
        
class ChatRoomModel(models.Model):
    vcChatRoomSerialNo = models.CharField(max_length=50, unique=True, verbose_name=u'群编号')
    vcName = models.CharField(max_length=50, verbose_name=u'群昵称')
    vcBase64Name = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'base64编码后的群昵称')
    vcWxUserSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'开群用户编号')
    vcWxManagerUserSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'群主的微信用户编号')
    vcRobotSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'机器人编号')
    vcApplyCodeSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'验证码编号')
    # 自定义关系属性
    member = models.ManyToManyField(MemberInfo, blank=True, verbose_name=u'群成员')
    serNum = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'库编号')

    class Meta:
        db_table = 'chatroom_info'
        verbose_name_plural = verbose_name = u'群信息'

class IntoChatRoomMessageModel(models.Model):
    """
    机器人入群消息表
    存储由创机器人被拉入群时返回的消息，此时由创机器人群功能并被开通，
    需要借助此表中的｀vcSerialNo｀字段经由批量开群接口开通机器人群功能。
    """
    vcSerialNo = models.CharField(max_length=50, verbose_name=u'拉群编号')
    vcRobotSerialNo = models.CharField(max_length=50, verbose_name=u'机器人编号')
    vcName = models.CharField(max_length=50, verbose_name=u'群昵称')   
    vcBase64Name = models.CharField(max_length=100, verbose_name=u'群base64编码后的昵称')    
    vcWxUserSerialNo = models.CharField(max_length=50, verbose_name=u'拉群用户的微信编号')  
    vcNickName = models.CharField(max_length=100, verbose_name=u'用户昵称')
    vcBase64NickName = models.CharField(max_length=100, verbose_name=u'用户base64编码后的昵称')
    vcHeadImgUrl = models.CharField(max_length=1000, verbose_name=u'用户头像')
    dtCreateDate = models.DateTimeField(verbose_name=u'创建时间')
    # 新填一个字段来表示该拉群编号是不是用于激活群成功（2017-7-14之前的无效）
    state = models.CharField(max_length=10, default=1, verbose_name=u'是否已经开群')

    class Meta:
        db_table = 'into_chatroom_message'
        verbose_name_plural = verbose_name = u'入群回调消息'
        
class IntoChatRoom(models.Model):
    """
    成员入群消息表
    """
    vcChatRoomSerialNo = models.CharField(max_length=50, verbose_name=u'群编号')
    vcWxUserSerialNo = models.CharField(max_length=50, verbose_name=u'用户编号')
    vcFatherWxUserSerialNo = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'用户父级编号（邀请人编号）')
    vcNickName = models.CharField(max_length=100, verbose_name=u'用户昵称')
    vcBase64NickName = models.CharField(max_length=100, verbose_name=u'Base64编码后的用户昵称')
    vcHeadImages = models.CharField(max_length=1000, verbose_name=u'用户头像')
    nJoinChatRoomType = models.CharField(max_length=5, verbose_name=u'入群方式')
    message_create_time = models.DateTimeField(default=timezone.now, verbose_name=u'消息获取时间')
    
    class Meta:
        db_table = 'into_chatroom'
        verbose_name_plural = verbose_name = u'成员入群消息'
        
class DropOutChatRoom(models.Model):
    """
    成员退群消息表
    """
    vcChatRoomSerialNo = models.CharField(max_length=50, verbose_name=u'群编号')
    vcWxUserSerialNo = models.CharField(max_length=50, verbose_name=u'用户编号')
    dtCreateDate = models.DateTimeField(verbose_name=u'退群时间')
    class Meta:
        db_table = 'drop_out_chatroom'
        verbose_name_plural = verbose_name = u'成员退群消息'

class ChatMessageModel(models.Model):
    vcSerialNo = models.CharField(max_length=50, verbose_name=u'消息编号')
    vcChatRoomSerialNo = models.CharField(max_length=50, verbose_name=u'群编号')
    vcFromWxUserSerialNo = models.CharField(max_length=50, verbose_name=u'发言人用户编号')
    dtMsgTime = models.DateTimeField(null=True, blank=True, verbose_name=u'消息时间')
    nMsgType = models.IntegerField(null=True, blank=True, verbose_name=u'消息类型')
    vcContent = models.TextField(null=True, blank=True, verbose_name=u'文本消息内容')
    nVoiceTime = models.CharField(max_length=5, null=True, blank=True, verbose_name=u'语音时长')
    vcShareTitle = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'链接标题')
    vcShareDesc = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'链接描述')
    vcShareUrl = models.CharField(max_length=1000, null=True, blank=True, verbose_name=u'链接url')
    
    class Meta:
        db_table = 'chatmessage'
        ordering = ['-dtMsgTime']
        verbose_name_plural = verbose_name = u'群内聊天信息'


class RoomTask(models.Model):
    task_id = models.CharField(max_length=50, verbose_name=u'建群任务编号')
    serNum = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'库编号')

    class Meta:
        db_table = 'roomtask'
        verbose_name_plural = verbose_name = u'建群任务信息'


class RobotChatRoom(models.Model):
    vcRobotSerialNo = models.CharField(max_length=50, verbose_name=u'机器人编号')
    vcChatRoomSerialNo = models.CharField(max_length=50, verbose_name=u'群编号')
    state = models.CharField(max_length=10, default=0, verbose_name=u'是否在群内')

    class Meta:
        db_table = 'robotchatroom'
        verbose_name_plural = verbose_name = u'机器人群信息'
