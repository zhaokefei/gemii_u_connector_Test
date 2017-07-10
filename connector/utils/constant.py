# /usr/bin/env python
# -*- coding:utf-8 -*-

class MsgConf(object):

    # 生产B redis
    redis_jbb_b = {
        'host': 'gemii-jbb.ldtntv.ng.0001.cnn1.cache.amazonaws.com.cn',
        'port': '6379',
        'password': '',
        'db': 0,
        'type': 'B'
    }

    # 生产A redis
    redis_wyeth_a = {
        'host': '54.223.132.253',
        'port': '8081',
        'password': 'gemii@123.cc',
        'db': 0,
        'type': 'A'
    }

    # 测试 redis
    redis_test = {
        'host': '54.223.198.95',
        'port': '8081',
        'password': 'gemii@123.cc',
        'db': 0,
        'type': 'B'
    }

    local_redis_a = {
        'host': 'localhost',
        'port': '8080',
        'password': '',
        'db': 0
    }

    local_redis_b = {
        'host': 'localhost',
        'port': '8081',
        'password': '',
        'db': 0

    }

