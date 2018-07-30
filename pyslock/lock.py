# -*- coding: utf-8 -*-
# 14-8-6
# create by: snower

from bson.objectid import ObjectId
from .command import Command
from .result import *


class LockException(Exception):
    pass


class LockLockedError(LockException):
    pass


class LockUnlockedError(LockException):
    pass


class LockIsLockingError(LockException):
    pass


class LockIsUnlockingError(LockException):
    pass


class LockTimeoutError(LockException):
    pass


class LockUnlockNotOwnError(LockException):
    pass


class Lock(object):
    def __init__(self, db, lock_name, timeout=0, expried=0, lock_id=None, max_count=1):
        self._db = db
        self._db_id = db.id
        self._lock_name = lock_name
        self._lock_id = lock_id or self.generate()
        self._timeout = timeout
        self._expried = expried
        self._lock = False
        self._max_count = max_count

    def generate(self):
        return ObjectId().binary + "\x00\x00\x00\x00"

    def acquire(self):
        if self._lock:
            raise LockLockedError()
        command = Command(Command.COMMAND_TYPE.LOCK, self._lock_id, self._db_id, self._lock_name, self._timeout, self._expried, 0, max(self._max_count - 1, 0))
        result = self._db.command(self, command)
        if not result:
            raise LockTimeoutError()
        self.on_result(result)

    def release(self):
        if not self._lock:
            raise LockUnlockedError()
        command = Command(Command.COMMAND_TYPE.UNLOCK, self._lock_id, self._db_id, self._lock_name, self._timeout, self._expried, 0, max(self._max_count - 1, 0))
        result = self._db.command(self, command)
        if not result:
            raise LockTimeoutError()
        self.on_result(result)

    def on_result(self, result):
        if result.command == Command.COMMAND_TYPE.LOCK:
            self.on_lock_result(result)
        elif result.command == Command.COMMAND_TYPE.UNLOCK:
            self.on_unlock_result(result)

    def on_lock_result(self, result):
        if result.result == RESULT_SUCCED:
            self._lock = True
            return result.result
        else:
            if result.result == RESULT_LOCKED_ERROR:
                raise LockLockedError()
            elif result.result == RESULT_TIMEOUT:
                raise LockTimeoutError()
            else:
                raise LockException()

    def on_unlock_result(self, result):
        if result.result == RESULT_SUCCED:
            self._lock = False
            return result.result
        else:
            if result.result == RESULT_UNLOCK_ERROR:
                raise LockUnlockedError()
            elif result.result == RESULT_UNOWN_ERROR:
                raise LockUnlockNotOwnError()
            else:
                raise LockException()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.release()
        except:
            pass