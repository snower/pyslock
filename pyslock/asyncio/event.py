# -*- coding: utf-8 -*-
# 18/8/3
# create by: snower

from ..utils import ensure_bytes
from .lock import Lock, LockLockedError, LockUnlockedError, LockTimeoutError
from ..protocol.exceptions import EventWaitTimeoutError


class Event(object):
    WaitTimeoutError = EventWaitTimeoutError

    def __init__(self, db, event_name, timeout=5, expried=65):
        self._db = db
        self._db_id = db.id
        self._event_name = ensure_bytes(event_name)
        self._event_id = ensure_bytes(event_name)
        self._event_lock = None
        self._check_lock = None
        self._wait_lock = None
        self._timeout = timeout
        self._expried = expried

    async def clear(self):
        if self._event_lock is None:
            self._event_lock = Lock(self._db, self._event_name, self._timeout, self._expried, self._event_id)

        try:
            await self._event_lock.acquire()
        except LockLockedError:
            pass
        return None

    async def set(self):
        if self._event_lock is None:
            self._event_lock = Lock(self._db, self._event_name, self._timeout, self._expried, self._event_id)

        try:
            await self._event_lock.release()
        except LockUnlockedError:
            pass

        return None

    async def is_set(self):
        self._check_lock = Lock(self._db, self._event_name, 0, 0)

        try:
            await self._check_lock.acquire()
        except LockTimeoutError:
            return False
        return True

    async def wait(self, timeout = 60):
        self._wait_lock = Lock(self._db, self._event_name, timeout, 0)

        try:
            await self._wait_lock.acquire()
        except LockTimeoutError:
            raise self.WaitTimeoutError()
        return True


class CycleEvent(Event):
    async def wait(self, timeout=60):
        self._wait_lock = Lock(self._db, self._event_name, timeout, 0)

        try:
            await self._wait_lock.acquire()
        except LockTimeoutError:
            if self._event_lock is None:
                self._event_lock = Lock(self._db, self._event_name, self._timeout, self._expried, self._event_id)
            try:
                await self._event_lock.acquire(0x02)
            except LockLockedError:
                raise self.WaitTimeoutError()

            try:
                await self._event_lock.release()
            except: pass
        return True