# -*- coding: utf-8 -*-
# 18/7/6
# create by: snower

import sys
import os
import random
import time
import hashlib
import socket
import struct
import threading

if sys.version_info[0] >= 3:
    py3 = True

    def ensure_bytes(s):
        if isinstance(s, str):
            return s.encode("utf-8")
        return s

    def ensure_unicode(s):
        if isinstance(s, bytes):
            try:
                return s.decode("utf-8")
            except UnicodeDecodeError:
                return s
        return s

    def bytetoint(b):
        return b
else:
    py3 = False

    def ensure_bytes(s):
        if isinstance(s, unicode):
            return s.encode("utf-8")
        return s

    def ensure_unicode(s):
        if isinstance(s, str):
            try:
                return s.encode("utf-8")
            except UnicodeDecodeError:
                return s
        return s

    bytetoint = ord

def _machine_bytes():
    machine_hash = hashlib.md5()
    if py3:
        machine_hash.update(socket.gethostname().encode())
    else:
        machine_hash.update(socket.gethostname())
    return machine_hash.digest()[0:6]

class UniqId(object):
    _inc = random.randint(0, 0xFFFFFF)
    _inc_lock = threading.Lock()
    _machine_bytes = _machine_bytes()

    def __init__(self):
        oid = struct.pack(">i", int(time.time()))
        oid += self._machine_bytes
        oid += struct.pack(">H", os.getpid() % 0xFFFF)
        with UniqId._inc_lock:
            oid += struct.pack(">i", UniqId._inc)
            UniqId._inc = (UniqId._inc + 1) % 0x7FFFFFFF

        self.__id = oid

    def to_bytes(self):
        return self.__id