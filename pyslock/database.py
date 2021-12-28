# -*- coding: utf-8 -*-
# 14-8-6
# create by: snower

import threading
from .lock import Lock
from .event import Event
from .semaphore import Semaphore
from .rwlock import RWLock
from .rlock import RLock

class DataBase(object):
    def __init__(self, client, db=0):
        self._client = client
        self._db = db
        self._lock = threading.Lock()
        self._locks = {}

    @property
    def id(self):
        return self._db

    def Lock(self, lock_name, timeout=0, expried=0):
        return Lock(self, lock_name, timeout, expried)

    def Event(self, event_name, timeout=0, expried=0, default_seted=True):
        return Event(self, event_name, timeout, expried, default_seted)

    def Semaphore(self, semaphore_name, timeout=0, expried=0, count=1):
        return Semaphore(self, semaphore_name, timeout, expried, count)

    def RWLock(self, lock_name, timeout=0, expried=0):
        return RWLock(self, lock_name, timeout, expried)

    def RLock(self, lock_name, timeout=0, expried=0):
        return RLock(self, lock_name, timeout, expried)

    def command(self, lock, command):
        connection = self._client.get_connection()
        event = threading.Event()
        self._locks[command.request_id] = event
        connection.write(command)
        succed = event.wait(max(command.timeout, 3) if command.timeout & 0x04000000 == 0 else int((command.timeout & 0xffff) / 1000 + 1))
        with self._lock:
            result = self._locks[command.request_id] if succed else None
            del self._locks[command.request_id]
        return result

    def on_result(self, result):
        if result.request_id in self._locks:
            with self._lock:
                event = self._locks[result.request_id]
                self._locks[result.request_id] = result
            event.set()
