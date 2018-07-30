# -*- coding: utf-8 -*-
# 18/7/6
# create by: snower

import sys

if sys.version_info[0] >= 3:
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

    def bytetoint(b):
        return ord(b)