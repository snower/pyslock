# -*- coding: utf-8 -*-
# 19/3/20
# create by: snower

from collections import deque
from .utils import ensure_bytes
from .lock import Lock, LockUnlockedError

class RWLock(object):
    def __init__(self, db, lock_name, timeout=0, expried=0):
        self._db = db
        self._db_id = db.id
        self._semaphore_name = ensure_bytes(lock_name)
        self._rlocks = deque()
        self._wlock = None
        self._timeout = timeout
        self._expried = expried

    async def racquire(self):
        lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, max_count=0x10000)
        await lock.acquire()
        self._rlocks.append(lock)

    async def rrelease(self):
        try:
            lock = self._rlocks.popleft()
        except IndexError:
            raise LockUnlockedError()
        else:
            await lock.release()

    async def acquire(self):
        if not self._wlock:
            self._wlock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, max_count=1)
        await self._wlock.acquire()

    async def release(self):
        if not self._wlock:
            raise LockUnlockedError()

        await self._wlock.release()