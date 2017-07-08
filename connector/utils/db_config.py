#!/usr/bin/python
# -*- coding: utf-8 -*-
import pymysql


class DBCONF(object):
    #todo change db

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

def print_file(char):
    with open("a.txt", "w") as f:
        print >> f, char
