# -*- coding: utf-8 -*-
# 19/3/20
# create by: snower

from collections import deque
from ..utils import ensure_bytes
from .lock import Lock, LockUnlockedError

class Semaphore(object):
    def __init__(self, db, semaphore_name, timeout=0, expried=60, count = 1):
        self._db = db
        self._db_id = db.id
        self._semaphore_name = ensure_bytes(semaphore_name)
        self._locks = deque()
        self._timeout = timeout
        self._expried = expried
        self._count = count

    async def acquire(self):
        lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, max_count=self._count)
        await lock.acquire()
        self._locks.append(lock)

    async def release(self):
        try:
            lock = self._locks.popleft()
        except IndexError:
            raise LockUnlockedError()
        else:
            await lock.release()