#!/usr/bin/python
# -*- coding: utf-8 -*-
import pymysql

# Test
CALLBACK_JAVA = "http://mt.gemii.cc/GroupManage/file/updateInfo"

# Product
# CALLBACK_JAVA = "http://jbb.gemii.cc/GroupManage/file/updateInfo"


class DBCONF(object):
    #todo change db

    # 生产B库两个
    wechat_gemii_config = {
        #test_db
        'host': "gemii.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn",
        # product_db
        # 'host': "wechatbot4jbb.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn",
        'user': "root",
        'password': "t721si74",
        'database': "wechat_gemii",
        'charset': 'utf8mb4',  # 支持1-4个字节字符
        'cursorclass': pymysql.cursors.DictCursor
    }

    wechat4bot2hye_config = {
        # test_db
        'host': "gemii.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn",
        # product_db
        # 'host': "wechatbot4jbb.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn",
        'user': "root",
        'password': "t721si74",
        # 'database': "wechat4bot2hye",
        'database': "wechat_bot",
        'charset': 'utf8mb4',  # 支持1-4个字节字符
        'cursorclass': pymysql.cursors.DictCursor
    }

    # 生产 A库 两个
    wechat_a_gemii = {
        # test_db
        'host': "gemii.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn",
        # product_db
        # 'host': "wechat4bot.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn",
        # 'database': "wechat",
        'user': "root",
        'password': "t721si74",
        # 'database': "wechat_bot",
        'charset': 'utf8mb4',  # 支持1-4个字节字符
        'cursorclass': pymysql.cursors.DictCursor
    }

    wechat_a_wyeth = {
        'host': "wechat4bot2wyeth.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn",
        'user': "root",
        'password': "t721si74",
        'database': "wechat",
        # 'database': "wechat_bot",
        'charset': 'utf8mb4',  # 支持1-4个字节字符
        'cursorclass': pymysql.cursors.DictCursor
    }




    local_config = {
        'host': "localhost",
        'user': "root",
        'password': "123456",
        'database': "wechat",
        'charset': 'utf8mb4',  # 支持1-4个字节字符
        'cursorclass': pymysql.cursors.DictCursor
    }

    test_config = {
        'host': "gemii.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn",
        'user': "root",
        'password': "t721si74",
        'database': "wechat_gemii",
        # 'database': "wechat4bot2hye",
        'charset': 'utf8mb4',  # 支持1-4个字节字符
        'cursorclass': pymysql.cursors.DictCursor
    }


class MsgConf(object):

    # 生产B redis
    redis_jbb_b = {
        ## Product
        # 'host': 'gemii-jbb.ldtntv.ng.0001.cnn1.cache.amazonaws.com.cn',
        # 'port': '6379',
        # 'password': '',
        # 'db': 0,
        # 'type': 'B'

        ## Test
        'host': '54.223.198.95',
        'port': '8081',
        'password': 'gemii@123.cc',
        'db': 0,
        'type': 'B'
    }

    # 生产A redis
    redis_wyeth_a = {
        ## Product
        # 'host': '54.223.132.253',
        # 'port': '8081',
        # 'password': 'gemii@123.cc',
        # 'db': 0,
        # 'type': 'A'

        ## Test
        'host': '54.223.198.95',
        'port': '8081',
        'password': 'gemii@123.cc',
        'db': 0,
        'type': 'B'
    }

    # 测试 redis
    redis_test = {
        'host': '54.223.198.95',
        'port': '8081',
        'password': 'gemii@123.cc',
        'db': 0,
        'type': 'B'
    }



def print_file(char):
    if isinstance(char, unicode):
        char = char.encode('utf-8')
    with open("a.txt", "w") as f:
        print >> f, char
