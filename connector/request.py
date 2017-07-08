# coding:utf-8
'''
Created on 2017年5月25日

@author: hepeng
'''
import requests

class BaseRequest(object):
    def __init__(self, host, method, headers):
        self.host = host
        self.method = method
        self.headers = headers
        self._data = None
        self._api = None
    @property
    def api(self):
        return self._api
    @api.setter
    def api(self, value):
        self._api = value
    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, value):
        self._data = value
    def request(self):
        url = self.host + self.api
        r = self.method(url, data=self.data, headers=self.headers)
        return r.content

class URequest(BaseRequest):
    def __init__(self):
        host = 'http://skyagent.shequnguanjia.com/'
        method = requests.post
        headers = {'content-type':'application/x-www-form-urlencoded'}
        super(URequest, self).__init__(host, method, headers)

class URequestVer2(BaseRequest):
    """
    由创建群系统request
    """
    def __init__(self, method=requests.post):
        host = 'http://schoolv2.17vsell.com/'
        method = method
        headers = {'content-type': 'application/json',
                   'uc-agent': 'o1o-PwC2bydkk1iasqeHIuQswS2I',
                   }
        super(URequestVer2, self).__init__(host, method, headers)
