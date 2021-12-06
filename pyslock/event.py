# -*- coding: utf-8 -*-
# 18/7/6
# create by: snower

from .utils import ensure_bytes
from .lock import Lock, LockLockedError, LockUnlockedError, LockTimeoutError, LockNotOwnError
from .protocol.exceptions import EventWaitTimeoutError

class Event(object):
    WaitTimeoutError = EventWaitTimeoutError

    def __init__(self, db, event_name, timeout=0, expried=60, default_seted=True):
        self._db = db
        self._db_id = db.id
        self._event_name = ensure_bytes(event_name)
        self._event_id = ensure_bytes(event_name)
        self._event_lock = None
        self._check_lock = None
        self._wait_lock = None
        self._timeout = timeout
        self._expried = expried
        self.default_seted = default_seted

    def clear(self):
        if self.default_seted:
            if self._event_lock is None:
                self._event_lock = Lock(self._db, self._event_name, self._timeout, self._expried, self._event_id, 0, 0)
            try:
                self._event_lock.acquire(0x02)
            except LockLockedError:
                pass
            return None

        if self._event_lock is None:
            self._event_lock = Lock(self._db, self._event_name, self._timeout, self._expried, self._event_id, 2, 0)
        try:
            self._event_lock.release()
        except LockUnlockedError:
            pass
        return None

    def set(self):
        if self.default_seted:
            if self._event_lock is None:
                self._event_lock = Lock(self._db, self._event_name, self._timeout, self._expried, self._event_id, 0, 0)
            try:
                self._event_lock.release()
            except LockUnlockedError:
                pass
            return None

        if self._event_lock is None:
            self._event_lock = Lock(self._db, self._event_name, self._timeout, self._expried, self._event_id, 2, 0)
        try:
            self._event_lock.acquire(0x02)
        except LockLockedError:
            pass
        return None

    def is_set(self):
        if self.default_seted:
            self._check_lock = Lock(self._db, self._event_name, 0, 0, 0, 0)
            try:
                self._check_lock.acquire()
            except LockTimeoutError:
                return False
            return True

        self._check_lock = Lock(self._db, self._event_name, 0x02000000, 0, 2, 0)
        try:
            self._check_lock.acquire()
        except LockTimeoutError:
            return False
        except LockNotOwnError:
            return False
        return True

    def wait(self, timeout=60):
        if self.default_seted:
            self._wait_lock = Lock(self._db, self._event_name, timeout, 0, 0, 0)
            try:
                self._wait_lock.acquire()
            except LockTimeoutError:
                raise self.WaitTimeoutError()
            return True

        self._wait_lock = Lock(self._db, self._event_name, timeout | 0x02000000, 0, 2, 0)
        try:
            self._wait_lock.acquire()
        except LockTimeoutError:
            raise self.WaitTimeoutError()
        return True

    def wait_and_timeout_retry_clear(self, timeout=60):
        if self.default_seted:
            self._wait_lock = Lock(self._db, self._event_name, timeout, 0, 0, 0)
            try:
                self._wait_lock.acquire()
            except LockTimeoutError:
                self._event_lock = Lock(self._db, self._event_name, self._timeout, self._expried, self._event_id, 0, 0)
                try:
                    self._event_lock.acquire(0x02)
                except LockLockedError:
                    raise self.WaitTimeoutError()
                try:
                    self._event_lock.release()
                except:
                    pass
            return True

        self._wait_lock = Lock(self._db, self._event_name, timeout | 0x02000000, 0, 2, 0)
        try:
            self._wait_lock.acquire()
        except LockTimeoutError:
            raise self.WaitTimeoutError()
        self._event_lock = Lock(self._db, self._event_name, self._timeout, self._expried, self._event_id, 2, 0)
        try:
            self._event_lock.release()
        except:
            pass
        return True