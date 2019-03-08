# -*- coding: utf-8 -*-
# 18/8/3
# create by: snower

from ..utils import UniqId
from asyncio import Future
from ..protocol.command import Command
from ..protocol.result import *
from ..protocol.exceptions import LockException, LockLockedError, LockUnlockedError, \
    LockIsLockingError, LockIsUnlockingError, LockTimeoutError, LockUnlockNotOwnError


class Lock(object):
    def __init__(self, db, lock_name, timeout=5, expried=8, lock_id = None, max_count = 1):
        self._db = db
        self._db_id = db.id
        self._lock_name = lock_name
        self._lock_id = lock_id or self.generate()
        self._timeout = timeout
        self._expried = expried
        self._max_count = max_count
        self._lock_future = None
        self._unlock_future = None

    def generate(self):
        return UniqId().to_bytes()

    def acquire(self, flag = 0):
        if self._lock_future:
            raise LockIsLockingError()

        self._lock_future = Future()
        command = Command(Command.COMMAND_TYPE.LOCK, self._lock_id, self._db_id, self._lock_name, self._timeout, self._expried, flag, max(self._max_count - 1, 0))
        def finish(future):
            self._lock_future = None
        self._lock_future.add_done_callback(finish)
        self._db.command(self, command, self._lock_future)
        return self._lock_future

    def release(self, flag = 0):
        if self._unlock_future:
            raise LockIsUnlockingError()

        self._unlock_future = Future()
        command = Command(Command.COMMAND_TYPE.UNLOCK, self._lock_id, self._db_id, self._lock_name, self._timeout, self._expried, flag, max(self._max_count - 1, 0))
        def finish(future):
            self._unlock_future = None
        self._unlock_future.add_done_callback(finish)
        self._db.command(self, command, self._unlock_future)
        return self._unlock_future

    def on_result(self, result):
        if result.command == Command.COMMAND_TYPE.LOCK:
            self.on_lock_result(result)
        elif result.command == Command.COMMAND_TYPE.UNLOCK:
            self.on_unlock_result(result)

    def on_lock_result(self, result):
        if result.result == RESULT_SUCCED:
            self._lock_future.set_result(result.result)
        else:
            if result.result == RESULT_LOCKED_ERROR:
                e = LockLockedError()
            elif result.result == RESULT_TIMEOUT:
                e = LockTimeoutError()
            else:
                e = LockException()
            self._lock_future.set_exception(e)

    def on_unlock_result(self, result):
        if result.result == RESULT_SUCCED:
            self._unlock_future.set_result(result.result)
        else:
            if result.result == RESULT_UNLOCK_ERROR:
                e = LockUnlockedError()
            elif result.result == RESULT_UNOWN_ERROR:
                e = LockUnlockNotOwnError()
            else:
                e = LockException()
            self._unlock_future.set_exception(e)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()