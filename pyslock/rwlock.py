# -*- coding: utf-8 -*-
# 19/3/20
# create by: snower

from collections import deque
from .utils import ensure_bytes
from .lock import Lock, Result, LockUnlockedError

class RWLock(object):
    def __init__(self, db, lock_name, timeout=0, expried=0):
        self._db = db
        self._db_id = db.id
        self._lock_name = ensure_bytes(lock_name)
        self._rlocks = deque()
        self._wlock = None
        self._timeout = timeout
        self._expried = expried

    def racquire(self):
        lock = Lock(self._db, self._lock_name, self._timeout, self._expried, max_count=0xffff)
        lock.acquire()
        self._rlocks.append(lock)

    def rrelease(self):
        try:
            lock = self._rlocks.popleft()
        except IndexError:
            raise LockUnlockedError(Result(b'\x56\x01' + b'\x00' * 62))
        else:
            lock.release()

    def acquire(self):
        if not self._wlock:
            self._wlock = Lock(self._db, self._lock_name, self._timeout, self._expried, max_count=1)
        self._wlock.acquire()

    def release(self):
        if not self._wlock:
            raise LockUnlockedError(Result(b'\x56\x01' + b'\x00' * 62))

        self._wlock.release()