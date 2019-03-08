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


class EventException(SlockException):
    pass


class EventWaitTimeoutError(Exception):
    pass