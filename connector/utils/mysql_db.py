#!/usr/bin/env python
# coding:utf-8

import pymysql
import threading
import logging

log = logging.getLogger('sql')

class MysqlDB:
    def __init__(self, conf):
        self.config = {
            'host': conf['host'],
            'user': conf['user'],
            'password': conf['password'],
            'database': conf['database'],
            'charset': 'utf8mb4',  # 支持1-4个字节字符
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.conn = pymysql.connect(**self.config)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def _trans_special_char(self, str1):
        if isinstance(str1, unicode):
            str1 = str1.encode('utf-8')
        str1 = str(str1)

        return str1.replace("\\", "\\\\").replace("\"", "\\\"").replace("\'", "\\\'")

    def _get_and_where(self, where_dict):
        """
        format sql condition string
        :param where_dict:
        :return:
        """
        return " and ".join(["%s='%s'" % (k, self._trans_special_char(v)) for k, v in where_dict.iteritems()])

    def _get_set(self, set_dict):
        """
        format sql update set string
        :param set_dict:
        :return:
        """
        return ",".join(["%s='%s'" % (k, self._trans_special_char(v)) for k, v in set_dict.iteritems()])

    def _get_fields_and_values(self, data_dict):
        """
        format insert field and value string
        :param data_dict:
        :return:
        """
        fields = []
        values = []
        for k, v in data_dict.iteritems():
            fields.append(k)
            values.append("'%s'" % self._trans_special_char(v))
        return ",".join(fields), ",".join(values)

    def insert(self, table, data_dict, ignore=False):
        """
        insert a record
        :param table:
        :param data_dict:
        :param ignore:  insert ignore
        :return:  last row id , cur.lastrowid
        """
        strsql = (ignore and "insert ignore" or "insert") + " into %s (%s) value (%s)"
        fields, values = self._get_fields_and_values(data_dict)
        strsql = strsql % (table, fields, values)
        if not values:
            return None
        self.lock.acquire()
        try:
            self.conn.ping(True)
            self.cursor.execute(strsql)
            res = self.cursor.lastrowid
            self.conn.commit()
            return res
        except Exception, e:
            log.info(strsql)
            log.info(e)
            return None
        finally:
            self.lock.release()

    def insert_many(self, table, data_dict_list, ignore=False):
        """

        :param table:
        :param data_dict_list:
        :return:
        """
        if not data_dict_list:
            return None
        fields = ",".join(data_dict_list[0].keys())
        values = [tuple(v.values()) for v in data_dict_list]
        strsql = (ignore and "insert ignore" or "insert") + " into %s (%s) value (%s)"
        strsql = strsql % (table, fields, ",".join(["%s"]*len(values[0])))
        try:
            self.lock.acquire()
            self.conn.ping(True)
            res = self.cursor.executemany(strsql, values)
            self.conn.commit()
            return res
        except Exception, e:
            log.info(e)
            return None
        finally:
            self.lock.release()

    def select(self, table, columns_list=[], where_dict={}):
        """
        select record
        :param table:
        :param columns_list:
        :param where_dict:
        :return: iter row & col
        """
        where = self._get_and_where(where_dict)
        fields = columns_list and ",".join(columns_list) or "*"
        strsql = "select %s from %s"
        strsql = where and (strsql + " where %s" % where) or strsql
        strsql = strsql % (fields, table)
        try:
            self.lock.acquire()
            self.conn.ping(True)
            self.cursor.execute(strsql)
            res = self.cursor.fetchall()
            self.conn.commit()
            return res
        except Exception, e:
            log.info(strsql)
            log.info(e)
            return None
        finally:
            self.lock.release()

    def update(self, table, set_dict, where_dict):
        """

        :param table:
        :param set_dict:
        :param where_dict:
        :return: affected rows number
        """
        set = self._get_set(set_dict)
        where = self._get_and_where(where_dict)
        strsql = "update %s set %s where %s" % (table, set, where)
        if set and where:
            return self.exec_sql(strsql)
        else:
            return None

    def delete(self, table, where_dict):
        """

        :param table:
        :param where_dict:
        :return:
        """
        where = self._get_and_where(where_dict)
        strsql = "delete from %s where %s" % (table, where)
        if where:
            log.info('sql:%s' % strsql)
            return self.exec_sql(strsql)
        else:
            return None

    def exec_sql(self, strsql):
        """
        write data, such as insert, delete, update
        :param strsql: string sql
        :return: affected rows number
        return 0 when errors
        """
        try:
            self.lock.acquire()
            self.conn.ping(True)
            res = self.cursor.execute(strsql)
            if strsql.strip().lower().startswith("select"):
                res = self.cursor.fetchall()
            self.conn.commit()
            return res
        except Exception, e:
            log.info(strsql)
            log.info(e)
            return 0
        finally:
            self.lock.release()

# local_config = {
#     'host': "localhost",
#     'user': "root",
#     'password': "123456",
#     'database': "wechat",
#     'charset': 'utf8mb4',  # 支持1-4个字节字符
#     'cursorclass': pymysql.cursors.DictCursor
# }
# mysql = MysqlDB(local_config)

