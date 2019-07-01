# -*- coding: utf-8 -*-
# 14-8-6
# create by: snower

import struct
from ..utils import UniqId
from ..utils import ensure_bytes

class Command(object):
    MAGIC = 0x56

    class COMMAND_TYPE:
        LOCK = 1
        UNLOCK = 2

    def __init__(self, command, lock_id, db_id, lock_name=None, timeout=0, expried=0, flag=0, count=0, rcount=0):
        self.version = 1
        self.request_id = self.generate()
        self.command = int(command)
        self.flag = flag
        self.lock_id = lock_id
        self.db_id = int(db_id)
        self.lock_name = ensure_bytes(lock_name)[:16]
        self.lock_name = ((16 - len(self.lock_name)) * b'\x00') + self.lock_name
        self.timeout = timeout
        self.expried = expried
        self.count = count
        self.rcount = rcount

    def generate(self):
        return UniqId().to_bytes()

    def dumps(self):
        return struct.pack("<BBB16sBB16s16sIIHB", self.MAGIC, self.version, self.command, ensure_bytes(self.request_id),
                           self.flag, self.db_id, ensure_bytes(self.lock_id), ensure_bytes(self.lock_name),
                           self.timeout, self.expried, self.count, self.rcount)