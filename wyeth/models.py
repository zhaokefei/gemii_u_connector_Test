# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class WeChatRoomInfo(models.Model):
    RoomID = models.CharField(max_length=100, primary_key=True)
    U_RoomID = models.CharField(max_length=255, null=True, blank=True)
    RoomName = models.CharField(max_length=255, null=True, blank=True)
    owner = models.CharField(max_length=50)

    class Meta:
        db_table = 'WeChatRoomInfo'


class WeChatRoomMessage(models.Model):
    MsgID = models.CharField(max_length=50, primary_key=True)
    Content = models.TextField()
    MsgType = models.IntegerField()
    AppMsgType = models.IntegerField()
    UserDisplayName = models.CharField(max_length=500, null=True, blank=True)
    CreateTime = models.DateTimeField()
    RoomID = models.CharField(max_length=100, null=True, blank=True)
    MemberID = models.CharField(max_length=100, null=True, blank=True)
    UserNickName = models.CharField(max_length=500, null=True, blank=True)
    MemberIcon = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'WeChatRoomMessage'


class WeChatRoomMemberInfo(models.Model):
    MemberID = models.AutoField(primary_key=True)
    RoomID = models.CharField(max_length=100)
    NickName = models.CharField(max_length=500, null=True, blank=True)
    U_UserID = models.CharField(max_length=255, null=True, blank=True)
    DisplayName = models.CharField(max_length=255, null=True, blank=True)
    open_id = models.CharField(max_length=100, null=True, blank=True)
    UserID = models.CharField(max_length=255, null=True, blank=True)
    member_icon = models.CharField(max_length=255, null=True, blank=True)
    is_legal = models.CharField(max_length=10)

    class Meta:
        db_table = 'WeChatRoomMemberInfo'


class UserInfo(models.Model):
    Openid = models.CharField(max_length=255, null=True, blank=True)
    U_UserID = models.CharField(max_length=255, null=True, blank=True)
    UserName = models.CharField(max_length=50, null=True, blank=True)
    MatchGroup = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'UserInfo'

class UserStatus(models.Model):
    PhoneCode = models.CharField(max_length=255, null=True, blank=True)
    UserID = models.CharField(max_length=255, null=True, blank=True)
    FriendStatus = models.CharField(max_length=255, null=True, blank=True)
    EnterGroupStatus = models.CharField(max_length=255, null=True, blank=True)
    userInfo = models.ForeignKey(UserInfo, db_column="FKUserInfoID", null=True,blank=True)
    ConfirmStatus = models.CharField(max_length=255, null=True, blank=True)
    GroupTime = models.CharField(max_length=255, null=True, blank=True)
    MatchStatus = models.CharField(max_length=255, null=True, blank=True)
    MatchGroup = models.CharField(max_length=255, null=True, blank=True)
    UserName = models.CharField(max_length=255, null=True, blank=True)
    Type = models.CharField(max_length=255, null=True, blank=True)
    FriendTime = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'UserStatus'




