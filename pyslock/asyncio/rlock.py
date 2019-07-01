# -*- coding: utf-8 -*-
# 2019/7/1
# create by: snower

from collections import deque
from ..utils import ensure_bytes
from .lock import Lock, LockUnlockedError, LockLockedError

class RLock(object):
    def __init__(self, db, lock_name, timeout=0, expried=60):
        self._db = db
        self._db_id = db.id
        self._lock_name = ensure_bytes(lock_name)
        self._locks = deque()
        self._timeout = timeout
        self._expried = expried

    async def acquire(self):
        if len(self._locks) >= 0xff:
            raise LockLockedError()

        lock = Lock(self._db, self._lock_name, self._timeout, self._expried, reentrant_count = 0xff)
        await lock.acquire()
        self._locks.append(lock)

    async def release(self):
        try:
            lock = self._locks.pop()
        except IndexError:
            raise LockUnlockedError()
        else:
            await lock.release()