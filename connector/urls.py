# coding:utf-8
'''
Created on 2017年5月8日

@author: hepeng
'''

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from connector.views import ChatMessageListView, URobotView, \
    ChatRoomView, IntoChatRoomMessageCreateView, IntoChatRoomCreateView, \
    DropOutChatRoomCreateView, MemberInfoCreateView, GetUrobotQucode, UnotityCallback, CreateRoomTaskView, \
    ChatRoomKickingView, CreateRoomCallbackView, ModifyRoomNameView, OpenKickingView, ShowKickingView, RebotRoomView, \
    Qrcode, RobotBlockedView, WhiteMemberCallBackView, SendMessageFailView, UpdateRoomMembers, RoomOver, \
    CheckChatRoomStatus, ChatRoomInfoModify, ChatRoomAdminChange
from django.views.decorators.csrf import csrf_exempt
from connector import views

router = DefaultRouter()
router.register(r'chatmessages', ChatMessageListView, base_name='chatmessages')
router.register(r'urobot', URobotView, base_name='urobot')
router.register(r'chatrooms', ChatRoomView, base_name='chatrooms')

urlpatterns = [
    url(r'', include(router.urls)),
    # 机器人入群回调
    url(r'intochatroommessage/$', IntoChatRoomMessageCreateView.as_view(), name='intochatroommessage'),
    # 成员入群
    url(r'intochatroom/$',IntoChatRoomCreateView.as_view(), name='intochatroom'),
    # 成员退群
    url(r'dropoutchatroom/$', DropOutChatRoomCreateView.as_view(), name='dropoutchatroom'),
    # 获取群成员回调
    url(r'memberinfo/$', csrf_exempt(MemberInfoCreateView.as_view()), name='memberinfo'),
]

urlpatterns += [
    url(r'^qrcode/$', csrf_exempt(GetUrobotQucode.as_view()), name='get_urobot_qrcode'),
    url(r'^unotity/callback/$', csrf_exempt(UnotityCallback.as_view()), name='unotity_callback'),
    # 建群任务
    url(r'^createroomtask/$', csrf_exempt(CreateRoomTaskView.as_view()), name="createroomtask"),
    url(r'^kickingchatroom/$', csrf_exempt(ChatRoomKickingView.as_view()), name='kickingmember'),
    # 建群成功回调
    url(r'^createroomdone/$', csrf_exempt(CreateRoomCallbackView.as_view()), name='createroomdone'),
    # 修改群名(java回调)
    url(r'^modifyroomname/$', csrf_exempt(ModifyRoomNameView.as_view()), name='modifyroomname'),
    url(r'^kickingtask/$', csrf_exempt(OpenKickingView.as_view()), name='kickingtask'),
    url(r'^showtask/$', csrf_exempt(ShowKickingView.as_view()), name='showtask'),
    # 机器人是否在群中回调
    url(r'^rebotroom/$', csrf_exempt(RebotRoomView.as_view()), name='rebotroom'),
    url(r'^make/qrcode/$', csrf_exempt(Qrcode.as_view()), name='make_qrcode'),
    # 机器人被封回调
    url(r'^robotblocked/$', csrf_exempt(RobotBlockedView.as_view()), name='robotblocked'),
    # 设置白名单成员
    url(r'^whitemember/$', csrf_exempt(WhiteMemberCallBackView.as_view()), name='whitemember'),
    # 消息发送失败接口回调
    url(r'^sendmsgfail/$', csrf_exempt(SendMessageFailView.as_view()), name='sendmsgfail'),

    # 提供给java - 获取群成员的接口
    url(r'^updateroommembers/$', csrf_exempt(UpdateRoomMembers.as_view()), name='updateroommembers'),
    # 提供给java - 注销群
    url(r'^roomover/$', csrf_exempt(RoomOver.as_view()), name='roomover'),
    # 提供给java - 查询群状态
    url(r'^checkchatroomstatus/$', csrf_exempt(CheckChatRoomStatus.as_view()), name='checkchatroomstatus'),
    # 提供给java - 修改群名
    url(r'^chatroominfomodify/$', csrf_exempt(ChatRoomInfoModify.as_view()), name='chatroominfomodify'),
    # 提供给java - 转让 群主
    url(r'^chatroomadminchange/$', csrf_exempt(ChatRoomAdminChange.as_view()), name='chatroomadminchange'),

]
