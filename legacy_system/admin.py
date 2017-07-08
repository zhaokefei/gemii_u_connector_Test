# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import RoomIdMap
# Register your models here.
class RoomIdMapAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_id', 'u_room_id')
admin.site.register(RoomIdMap, RoomIdMapAdmin)
