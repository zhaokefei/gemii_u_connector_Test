#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import traceback
import sys
from functools import wraps
from django.utils.decorators import available_attrs
from django.http.response import HttpResponse

view_log = logging.getLogger('view')

def view_exception_handler(view_func):
    """
    view异常处理
    """

    def wrapped_view(self,request,*args, **kwargs):

        try:
            return view_func(self,request,*args, **kwargs)
        except Exception,e:
            if 'strContext' in request.data:
                datas = request.data['strContext']
                view_log.info('accept strContext data:')
                view_log.info(datas)
            view_log.info(traceback.format_exc())
            return HttpResponse('SUCCESS')

    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)