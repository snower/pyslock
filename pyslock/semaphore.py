# -*- coding: utf-8 -*-
# 19/3/15
# create by: snower

from .utils import ensure_bytes
from .lock import Lock, LockUnlockedError, LockNotOwnError, LockTimeoutError

class Semaphore(object):
    def __init__(self, db, semaphore_name, timeout=0, expried=60, count = 1):
        self._db = db
        self._db_id = db.id
        self._semaphore_name = ensure_bytes(semaphore_name)
        self._timeout = timeout
        self._expried = expried
        self._count = count

    def acquire(self):
        lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, max_count=self._count)
        lock.acquire()

    def release(self, n = 1):
        if n == 1:
            try:
                lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, max_count=self._count)
                lock.release(0x01)
            except (LockUnlockedError, LockNotOwnError):
                return 0
            return 1

        lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, lock_id=b'\x00' * 16, max_count=self._count)
        for i in range(n):
            try:
                lock.release(0x01)
            except (LockUnlockedError, LockNotOwnError):
                return i + 1
        return n

    def release_all(self):
        n = 0
        lock = Lock(self._db, self._semaphore_name, self._timeout, self._expried, lock_id=b'\x00' * 16, max_count=self._count)
        while True:
            try:
                lock.release(0x01)
            except (LockUnlockedError, LockNotOwnError):
                return n + 1
            n += 1
        return n

    def count(self):
        lock = Lock(self._db, self._semaphore_name, 0, 0, max_count=self._count)
        try:
            lock.acquire(0x01)
        except LockUnlockedError:
            return 0
        except LockNotOwnError as e:
            return e.result.lcount
        except LockTimeoutError:
            return self._count
        return 0