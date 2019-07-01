# -*- coding: utf-8 -*-
# 2019/7/1
# create by: snower

from collections import deque
from .utils import ensure_bytes
from .lock import Lock, LockUnlockedError, LockLockedError

class RLock(object):
    def __init__(self, db, semaphore_name, timeout=0, expried=60):
        self._db = db
        self._db_id = db.id
        self._semaphore_name = ensure_bytes(semaphore_name)
        self._locks = deque()
        self._timeout = timeout
        self._expried = expried

    def acquire(self):
        if len(self._locks) >= 0xff:
            raise LockLockedError()

        lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, reentrant_count = 0xff)
        lock.acquire()
        self._locks.append(lock)

    def release(self):
        try:
            lock = self._locks.pop()
        except IndexError:
            raise LockUnlockedError()
        else:
            lock.release()