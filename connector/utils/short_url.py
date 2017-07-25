#!/usr/bin/python
# -*- coding: utf-8 -*-


import json
import requests
import time
import logging
import traceback
from urllib import quote

log = logging.getLogger('sql')

def get_short_url_from_sina(url):
    '''
    get shor_url from sina
    '''
    flag = 0
    if isinstance(url, unicode):
        url = url.encode('utf-8')
    while flag < 3:
        try:
            data = get('http://wx.gemii.cc/wx/long2short?long_url=%s' % quote(url))
            data = json.loads(data)
        except:
            log.info('获取短链fault')
            log.info(traceback.format_exc())
            return ''
        else:
            if data:
                short_url = str(data.get('data').get('short_url'))
                if short_url != 'http://t.cn/':
                    log.info('获取短链success')
                    return short_url
            flag += 1
            time.sleep(1)


def get(url):
    """
    @brief      http get request
    @param      url   String
    @param      api   wechat api
    @return     http response
    """
    headers = {
        'User-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Referer': 'https://wx.qq.com/',
        'Connection': 'keep-alive'
    }
    try_times = 0
    data = None
    while try_times < 2:
        try:
            data = requests.session().get(url, headers=headers, timeout=40).content
            return data
        except Exception as ex:
            log.info(traceback.format_exc())
        try_times += 1
    return data

if __name__ == '__main__':
    print get_short_url_from_sina('http://wx.gemii.cc/gemii/toPage.html?appid=wxc34006e5a93af3dd&scope=snsapi_base&state=&redirect_uri=http://mt.gemii.cc/gemii/card-web/index.html?info=云南-昆明-一心堂药店连锁-4')