# -*- coding: utf-8 -*-
# 2019/7/1
# create by: snower

from .utils import ensure_bytes
from .lock import Lock, LockUnlockedError, LockLockedError

class RLock(object):
    def __init__(self, db, lock_name, timeout=0, expried=60):
        self._db = db
        self._db_id = db.id
        self._lock_name = ensure_bytes(lock_name)
        self._timeout = timeout
        self._expried = expried

        self._lock = Lock(db, lock_name, timeout, expried, reentrant_count = 0xff)
        self._locked_count = 0

    def acquire(self):
        if self._locked_count >= 0xff:
            raise LockLockedError()

        self._lock.acquire()
        self._locked_count += 1

    def release(self):
        if self._locked_count == 0:
            raise LockUnlockedError()

        self._locked_count -= 1
        self._lock.release()