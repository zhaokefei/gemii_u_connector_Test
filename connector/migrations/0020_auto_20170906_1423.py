# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-06 14:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0019_auto_20170828_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='intochatroommessagemodel',
            name='vcChatRoomSerialNo',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u7fa4\u7f16\u53f7'),
        ),
        migrations.AlterField(
            model_name='intochatroommessagemodel',
            name='vcBase64Name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u7fa4base64\u7f16\u7801\u540e\u7684\u6635\u79f0'),
        ),
        migrations.AlterField(
            model_name='intochatroommessagemodel',
            name='vcBase64NickName',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u7528\u6237base64\u7f16\u7801\u540e\u7684\u6635\u79f0'),
        ),
        migrations.AlterField(
            model_name='intochatroommessagemodel',
            name='vcHeadImgUrl',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u7528\u6237\u5934\u50cf'),
        ),
        migrations.AlterField(
            model_name='intochatroommessagemodel',
            name='vcName',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u7fa4\u6635\u79f0'),
        ),
        migrations.AlterField(
            model_name='intochatroommessagemodel',
            name='vcNickName',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u7528\u6237\u6635\u79f0'),
        ),
        migrations.AlterField(
            model_name='intochatroommessagemodel',
            name='vcRobotSerialNo',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u673a\u5668\u4eba\u7f16\u53f7'),
        ),
        migrations.AlterField(
            model_name='intochatroommessagemodel',
            name='vcWxUserSerialNo',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u62c9\u7fa4\u7528\u6237\u7684\u5fae\u4fe1\u7f16\u53f7'),
        ),
    ]
