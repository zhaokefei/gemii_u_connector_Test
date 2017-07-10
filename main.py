# /usr/bin/env python
# -*- coding:utf-8 -*-

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UConnector.settings")
import django
django.setup()
import time
import signal
import logging

from django.conf import settings

from connector.send_message_thread import DataReceiveThread

running = True


def action(signum, frame):
    global running
    running = False

if __name__ == '__main__':

    signal.signal(signal.SIGINT, action)
    signal.signal(signal.SIGTERM, action)

    threads = []
    threads.append(DataReceiveThread('线程B', settings.REDIS_CONFIG['redis_b']))
    threads.append(DataReceiveThread('线程A', settings.REDIS_CONFIG['redis_a']))

    for thread in threads:
        thread.start()

    while running:
        time.sleep(1)

    for thread in threads:
        thread.stop()

    logging.info("shutdown.")