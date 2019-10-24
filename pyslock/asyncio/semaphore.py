# -*- coding: utf-8 -*-
# 19/3/20
# create by: snower

from ..utils import ensure_bytes
from .lock import Lock, LockNotOwnError, LockTimeoutError

class Semaphore(object):
    def __init__(self, db, semaphore_name, timeout=0, expried=60, count = 1):
        self._db = db
        self._db_id = db.id
        self._semaphore_name = ensure_bytes(semaphore_name)
        self._timeout = timeout
        self._expried = expried
        self._count = count

    async def acquire(self):
        lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, max_count=self._count)
        await lock.acquire()

    async def release(self, n=1):
        if n == 1:
            try:
                lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, max_count=self._count)
                await lock.release(0x01)
            except LockNotOwnError:
                return 0
            return 1

        for i in range(n):
            lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, lock_id=b'\x00' * 16, max_count=self._count)
            try:
                await lock.release(0x01)
            except LockNotOwnError:
                return i + 1
        return n

    async def release_all(self):
        n = 0
        lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, lock_id=b'\x00' * 16, max_count=self._count)
        while True:
            try:
                await lock.release(0x01)
            except LockNotOwnError:
                return n + 1
            n += 1
        return n

    async def count(self):
        lock = Lock(self._db, self._semaphore_name, 0, 0, max_count=self._count)
        try:
            await lock.acquire(0x01)
        except LockNotOwnError as e:
            return e.result.lcount
        except LockTimeoutError:
            return self._count
        return 0