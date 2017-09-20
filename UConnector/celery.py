#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
# 设置这个环境变量是为了让 celery 命令能找到 Django 项目
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UConnector.settings')

# app = Celery('gemii_u_connector_Test')
# 这个 app 就是 Celery 实例。
app = Celery('UConnector')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
# 通常是在单独的 tasks.py 中定义任务。Celery 会自动发现这些模块。
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

