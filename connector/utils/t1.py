#!/usr/bin/python
# -*- coding: utf-8 -*-

from connector.utils.mysql_db import MysqlDB
from connector.utils.db_config import DBCONF


def test_db():
    mysql = MysqlDB(DBCONF.local_config)
    print mysql.update('UserStatus', {'Type': 'A'}, {"id": 2930})

if __name__ == '__main__':
    test_db()