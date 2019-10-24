# -*- coding: utf-8 -*-
# 19/3/8
# create by: snower

class SlockException(Exception):
    pass


class ConnectionException(Exception):
    pass


class ConnectTimeOutError(Exception):
    pass


class ConnectionClosedError(Exception):
    pass


class ProtocolException(Exception):
    pass


class ProtocolResultDataIllegalError(Exception):
    pass


class LockException(SlockException):
    def __init__(self, result, *args, **kwargs):
        self.result = result
        super(LockException, self).__init__(*args, **kwargs)

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

class LockExpriedError(LockException):
    pass

class LockNotOwnError(LockException):
    pass


class EventException(SlockException):
    pass


class EventWaitTimeoutError(SlockException):
    pass