# -*- coding: utf-8 -*-
# 18/7/30
# create by: snower

from .database import DataBase
from .connection import Connection
from .pool import ConnectionPool

class Client(object):
    def __init__(self, host, port=5658, db_range = 256, max_connection = 1, reader_factory = None):
        def reader_factory_func(connection):
            if reader_factory is None:
                from .reader import Reader
                return Reader(self, connection)

            return reader_factory(self, connection)

        if max_connection == 1:
            self._connection = Connection(host, port, reader_factory_func)
            self._connection.reader.start()
            self._connection_pool = None
        else:
            self._connection = None
            self._connection_pool = ConnectionPool(host, port, max_connection, reader_factory_func)

        self._dbs = [None for _ in range(db_range)]
        self.select(0)

    def Lock(self, lock_name, timeout=0, expried=0, max_count=1):
        db = self.select(0)
        return db.Lock(lock_name, timeout, expried, max_count=max_count)

    def Event(self, event_name, timeout=0, expried=0):
        db = self.select(0)
        return db.Event(event_name, timeout, expried)

    def select(self, db=0):
        if db >= len(self._dbs):
            return None

        if self._dbs[db] is None:
            database = DataBase(self, db)
            self._dbs[db] = database
        return self._dbs[db]

    def get_connection(self):
        if self._connection:
            return self._connection

        return self._connection_pool.get_connection()

    def on_result(self, result):
        db = self.select(result.db_id)
        db.on_result(result)