# -*- coding: utf-8 -*-
# 18/8/3
# create by: snower

from .lock import Lock, Result, LockIsLockingError
from .event import Event
from ..protocol.exceptions import ConnectionClosedError
from .semaphore import Semaphore
from .rwlock import RWLock
from .rlock import RLock

class DataBase(object):
    def __init__(self, client, db=0):
        self._client = client
        self._db = db
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

    def command(self, lock, command, future):
        if command.request_id in self._locks:
            raise LockIsLockingError(Result(b'\x56\x01' + b'\x00' * 62))

        self._locks[command.request_id] = lock

        def finish(future):
            if command.request_id in self._locks:
                del self._locks[command.request_id]

        future.add_done_callback(finish)
        return self._client.get_connection().write(command, future)

    def on_result(self, result):
        if result.request_id in self._locks:
            lock = self._locks.get(result.request_id, None)
            if not lock:
                return
            lock.on_result(result)

    def on_connection_close(self):
        for _, lock in self._locks.items():
            if lock._lock_future:
                lock._lock_future.set_exception(ConnectionClosedError())
            if lock._unlock_future:
                lock._unlock_future.set_exception(ConnectionClosedError())