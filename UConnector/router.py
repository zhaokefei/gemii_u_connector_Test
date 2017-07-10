# /usr/bin/env python
# -*- coding:utf-8 -*-

class AuthRouter(object):
    """
        A router to control all database operations on models in the
        auth application.
        """

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == 'wechat':
            return 'gemii'
        elif model._meta.app_label == 'wyeth':
            return 'wyeth'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label == 'wechat':
            return 'gemii'
        elif model._meta.app_label == 'wyeth':
            return 'wyeth'

        return None


