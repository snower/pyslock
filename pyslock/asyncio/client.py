# -*- coding: utf-8 -*-
# 18/8/3
# create by: snower

from .database import DataBase
from .connection import Connection


class AsyncClient(object):
    def __init__(self, host, port=5658, db_range = 256):
        self._connection = Connection(self, host, port)
        self._dbs = [None for _ in range(db_range)]
        self.select(0)

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
        return self._connection

    def on_result(self, result):
        db = self.select(result.db_id)
        db.on_result(result)

    def on_connection_close(self):
        for db in self._dbs:
            if not db:
                continue
            db.on_connection_close()