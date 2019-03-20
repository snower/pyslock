# -*- coding: utf-8 -*-
# 18/7/30
# create by: snower

from .database import DataBase
from .connection import Connection

class Client(object):
    def __init__(self, host, port=5658, db_range = 256, reader_factory = None):
        def reader_factory_func(connection):
            if reader_factory is None:
                from .reader import Reader
                return Reader(self, connection)

            return reader_factory(self, connection)

        self._connection = Connection(host, port, reader_factory_func)
        self._dbs = [None for _ in range(db_range)]
        self._reader_stared = False

    def Lock(self, lock_name, timeout=0, expried=0):
        db = self.select(0)
        return db.Lock(lock_name, timeout, expried)

    def Event(self, event_name, timeout=0, expried=0):
        db = self.select(0)
        return db.Event(event_name, timeout, expried)

    def CycleEvent(self, event_name, timeout=0, expried=0):
        db = self.select(0)
        return db.CycleEvent(event_name, timeout, expried)

    def Semaphore(self, semaphore_name, timeout=0, expried=0, count=1):
        db = self.select(0)
        return db.Semaphore(semaphore_name, timeout, expried, count)

    def RWLock(self, lock_name, timeout=0, expried=0):
        db = self.select(0)
        return db.RWLock(lock_name, timeout, expried)

    def select(self, db=0):
        if db >= len(self._dbs):
            return None

        if self._dbs[db] is None:
            database = DataBase(self, db)
            self._dbs[db] = database
        return self._dbs[db]

    def get_connection(self):
        if not self._reader_stared:
            self._connection.reader.start()
            self._reader_stared = True
        return self._connection

    def on_result(self, result):
        db = self.select(result.db_id)
        db.on_result(result)