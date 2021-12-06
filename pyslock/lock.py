# -*- coding: utf-8 -*-
# 14-8-6
# create by: snower

from .utils import UniqId
from .protocol.command import Command
from .protocol.result import *
from .protocol.exceptions import LockException, LockLockedError, LockUnlockedError, \
    LockTimeoutError, LockExpriedError, LockNotOwnError

ERRORS = {
    5: LockLockedError,
    6: LockUnlockedError,
    7: LockNotOwnError,
    8: LockTimeoutError,
    9: LockExpriedError,
}

class Lock(object):
    def __init__(self, db, lock_name, timeout=0, expried=0, lock_id=None, max_count=1, reentrant_count = 0):
        self._db = db
        self._db_id = db.id
        self._lock_name = lock_name
        self._lock_id = lock_id or self.generate()
        self._timeout = timeout
        self._expried = expried
        self._max_count = max_count
        self._reentrant_count = reentrant_count

    def generate(self):
        return UniqId().to_bytes()

    def acquire(self, flag=0):
        command = Command(Command.COMMAND_TYPE.LOCK, self._lock_id, self._db_id, self._lock_name, self._timeout,
                          self._expried, flag, max(self._max_count - 1, 0), max(self._reentrant_count - 1, 0))
        result = self._db.command(self, command)
        if not result:
            raise LockTimeoutError(Result(b'\x56\x01' + b'\x00' * 62))
        self.on_result(result)

    def release(self, flag = 0):
        command = Command(Command.COMMAND_TYPE.UNLOCK, self._lock_id, self._db_id, self._lock_name, self._timeout,
                          self._expried, flag, max(self._max_count - 1, 0), max(self._reentrant_count - 1, 0))
        result = self._db.command(self, command)
        if not result:
            raise LockTimeoutError(Result(b'\x56\x01' + b'\x00' * 62))
        self.on_result(result)

    def on_result(self, result):
        if result.command == Command.COMMAND_TYPE.LOCK:
            self.on_lock_result(result)
        elif result.command == Command.COMMAND_TYPE.UNLOCK:
            self.on_unlock_result(result)

    def on_lock_result(self, result):
        if result.result == RESULT_SUCCED:
            return result
        else:
            if result.result in ERRORS:
                raise ERRORS[result.result](result)
            else:
                raise LockException(result)

    def on_unlock_result(self, result):
        if result.result == RESULT_SUCCED:
            return result
        else:
            if result.result in ERRORS:
                raise ERRORS[result.result](result)
            else:
                raise LockException(result)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()