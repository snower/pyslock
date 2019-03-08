# -*- coding: utf-8 -*-
# 14-8-6
# create by: snower


from ..utils import ensure_unicode, bytetoint
from .exceptions import ProtocolResultDataIllegalError


RESULT_SUCCED = 0
RESULT_UNKNOWN_MAGIC = 1
RESULTD_UNKNOWN_VERSION = 2
RESULT_UNKNOWN_DB = 3
RESULTD_UNKNOWN_COMMAND = 4
RESULT_LOCKED_ERROR = 5
RESULT_UNLOCK_ERROR = 6
RESULT_UNOWN_ERROR = 7
RESULT_TIMEOUT = 8
RESULT_EXPRIED = 9
RESULT_ERROR = 10

class Result(object):
    MAGIC = 0x56

    def __init__(self, data):
        if len(data) != 64:
            raise ProtocolResultDataIllegalError()

        self.magic = bytetoint(data[0])
        if self.magic != self.MAGIC:
            raise ProtocolResultDataIllegalError()

        self.version = bytetoint(data[1])
        self.command = bytetoint(data[2])
        self.request_id = data[3:19]
        self.result = bytetoint(data[19])
        self.flag = bytetoint(data[20])
        self.db_id = bytetoint(data[21])
        self.lock_id = data[22:38]
        self.lock_name = ensure_unicode(data[38:54])
