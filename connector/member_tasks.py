# encoding:utf-8
from __future__ import unicode_literals

import json
import copy

import logging

from celery.task import task

from wyeth.models import UserInfo
from wechat.models import WeChatRoomInfoGemii

from connector.utils.commont_tool import decode_base64, emoji_to_unicode, time_strf

member_log = logging.getLogger(str('member'))


def _choice_gemii(ab):
    return 'gemii' if ab == 'A' else 'gemii_b'


def _choice_wyeth(ab):
    return 'wyeth' if ab == 'A' else 'wyeth_b'


def watch(f):
    def _wrap(*args, **kwargs):
        import time
        t = time.time()
        r = f(*args, **kwargs)
        member_log.info('%s, %s' % (f.__name__, time.time()-t))
        return r
    return _wrap


@watch
def _sync_u_connector(data):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.callproc('sync_memberinfo', (data,))
        serNum = cursor.fetchone()[0]
        cursor.nextset()
        whitelist = [x[0] for x in cursor.fetchall()]
        return serNum, whitelist


def _get_roomid(ab, sn):
    try:
        return WeChatRoomInfoGemii.objects.using(_choice_gemii(ab))\
                .get(U_RoomID=sn).RoomID
    except WeChatRoomInfoGemii.DoesNotExist:
        pass


def _bind_userinfo(ab, roomid, whitelist, members):

    ids = [x['vcSerialNo'] for x in members]
    users = {}
    for user in UserInfo.objects.using(_choice_wyeth(ab)).filter(
            U_UserID__in=ids,
            MatchGroup=roomid):
        users[user.U_UserID] = (user.id, user.Openid)
    gemii_items = []
    wyeth_items = []
    for member in members:
        sn = member['vcSerialNo']
        item = {
                'NickName': member['vcNickName'],
                'U_UserID': sn,
                'member_icon': member['vcHeadImages'],
                'DisplayName': member['vcNickName'],
            }
        hasUser = sn in users
        if hasUser:
            t = users[sn]
            item['open_id'] = t[1]
            item['UserID'] = str(t[0])
        # 除A库之外
        if ab != 'A' and not hasUser:
            item['is_legal'] = '0'
        if sn in whitelist:
            item['is_legal'] = '2'
        # 珂飞添加is_legal == '1'
        if not item.get('is_legal'):
            item['is_legal'] = '1'
        wyeth_items.append(item)

        item = copy.copy(item)
        item['MemberID'] = sn
        # 珂飞添加时间转换
        item['enter_group_time'] = str(time_strf(member['dtCreateDate']))
        gemii_items.append(item)
    return gemii_items, wyeth_items


@watch
def _sync_room_memberinfo(ab, sn, roomid, items, is_gemii):
    from django.db import connections
    import json
    data = {'sn': sn, 'roomid': roomid, 'items': items}
    data = json.dumps(data)
    db_alias = _choice_gemii(ab) if is_gemii else _choice_wyeth(ab)
    member_log.info('database %s' % db_alias)
    with connections[db_alias].cursor() as cursor:
        cursor.callproc('sync_room_memberinfo', (data,))

@task
def sync_room_members(obj):
    # patch emoji
    # obj = json.loads(SRC, strict=False)
    sn = obj['vcChatRoomSerialNo']
    members = obj['Data'][0]['ChatRoomUserData']
    member_log.info('需要更新群 %s (%s) 个群成员数据' % (sn, len(members)))
    for member in members:
        nickname = decode_base64(member['vcBase64NickName'])\
                    .decode('utf-8')\
                    .strip('\n')
        member['vcNickName'] = emoji_to_unicode(nickname)
    data = json.dumps(obj)
    ab, whitelist = _sync_u_connector(data)
    member_log.info('更新connector库成功，选择更新数据至 %s 库' % ab)

    roomid = _get_roomid(ab, sn)
    if not roomid:
        member_log.info('没有匹配到对应的群信息，停止更新')
        return
    member_log.info('RoomID编号为 %s' % roomid)

    # bind userinfo
    gemii_items, wyeth_items = _bind_userinfo(ab, roomid, whitelist, members)

    _sync_room_memberinfo(ab, sn, roomid, gemii_items, True)
    _sync_room_memberinfo(ab, sn, roomid, wyeth_items, False)



