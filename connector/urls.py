# coding:utf-8
'''
Created on 2017年5月8日

@author: hepeng
'''

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import ChatMessageListView, URobotView, \
ChatRoomView, IntoChatRoomMessageCreateView, IntoChatRoomCreateView,\
DropOutChatRoomCreateView, MemberInfoCreateView, GetUrobotQucode, UnotityCallback, CreateRoomTaskView, \
ChatRoomKickingView, CreateRoomCallbackView, ModifyRoomNameView, OpenKickingView, ShowKickingView
from django.views.decorators.csrf import csrf_exempt

router = DefaultRouter()
router.register(r'chatmessages', ChatMessageListView, base_name='chatmessages')
router.register(r'urobot', URobotView, base_name='urobot')
router.register(r'chatrooms', ChatRoomView, base_name='chatrooms')

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'intochatroommessage/$', IntoChatRoomMessageCreateView.as_view(), name='intochatroommessage'),
    url(r'intochatroom/$',IntoChatRoomCreateView.as_view(), name='intochatroom'),
    url(r'dropoutchatroom/$', DropOutChatRoomCreateView.as_view(), name='dropoutchatroom'),
    url(r'memberinfo/$', MemberInfoCreateView.as_view(), name='memberinfo'),
]

urlpatterns += [
    url(r'^qrcode/$', csrf_exempt(GetUrobotQucode.as_view()), name='get_urobot_qrcode'),
    url(r'^unotity/callback/$', csrf_exempt(UnotityCallback.as_view()), name='unotity_callback'),
    url(r'^createroomtask/$', csrf_exempt(CreateRoomTaskView.as_view()), name="createroomtask"),
    url(r'^kickingchatroom/$', csrf_exempt(ChatRoomKickingView.as_view()), name='kickingmember'),
    url(r'^createroomdone/$', csrf_exempt(CreateRoomCallbackView.as_view()), name='createroomdone'),
    url(r'^modifyroomname/$', csrf_exempt(ModifyRoomNameView.as_view()), name='modifyroomname'),
    url(r'^kickingtask/$', csrf_exempt(OpenKickingView.as_view()), name='kickingtask'),
    url(r'^showtask/$', csrf_exempt(ShowKickingView.as_view()), name='showtask'),
]
