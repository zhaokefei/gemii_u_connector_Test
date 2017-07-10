# /usr/bin/env python
# -*- coding:utf-8 -*-

# -*- coding:utf-8 -*-

import logging
import sys
import threading

# from connector.data_receive_thread import DataReceiveThread
from connector.send_message_thread import DataReceiveThread

from connector.utils.constant import MsgConf

message_log = logging.getLogger('message')


def quit(signum, frame):
    sys.exit()


def run_once_time():
    try:
        # 设置`ctrl+c`安全退出
        #       signal.signal(signal.SIGINT, quit)
        #       signal.signal(signal.SIGTERM, quit)

        # 生产
        # message_thread_b = DataReceiveThread('线程B', MsgConf.redis_jbb_b)
        # message_thread_b.setDaemon(True)
        #
        # message_thread_a = DataReceiveThread('线程A', MsgConf.redis_wyeth_a)
        # message_thread_a.setDaemon(True)

        # message_thread_a.start()
        # message_thread_b.start()

        # message_log.info('当前线程为:%s ' % threading.current_thread())
        message_thread_b = DataReceiveThread('线程B', MsgConf.redis_test)
        message_thread_b.setDaemon(True)

        message_thread_a = DataReceiveThread('线程A', MsgConf.redis_test)
        message_thread_a.setDaemon(True)

        message_thread_a.start()
        message_thread_b.start()

        message_log.info('线程为:%s ' % threading.enumerate())

    except Exception, exc:
        message_log.info(exc)
        message_log.info('线程出错')


import pymysql

pymysql.install_as_MySQLdb()
