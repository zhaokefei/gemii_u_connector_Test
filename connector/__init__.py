#-*- coding:utf-8 -*-
import signal, sys, threading
from data_receive_thread import DataReceiveThread

def quit(signum, frame):
    sys.exit()

def run_once_time():
    try:
        # 设置`ctrl+c`安全退出
        print "hhhhhh"
 #       signal.signal(signal.SIGINT, quit)
 #       signal.signal(signal.SIGTERM, quit)
    
        message_thread = DataReceiveThread()
        message_thread.setDaemon(True)
        message_thread.start()
        print threading.current_thread()
    
    except Exception, exc:
        print exc

import pymysql
pymysql.install_as_MySQLdb()
