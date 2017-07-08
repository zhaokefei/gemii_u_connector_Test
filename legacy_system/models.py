# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class RoomIdMap(models.Model):
    """
    由创群id<->景栗群id映射表
    """
    room_id = models.CharField(max_length=50, verbose_name=u'景栗群id')
    u_room_id = models.CharField(max_length=50, verbose_name=u'由创群id')
    name = models.CharField(max_length=20, verbose_name=u'群名')
    
    class Meta:
        db_table = 'room_id_map'
        verbose_name_plural = verbose_name = u'群id映射表'