# -*- coding: utf-8 -*-
# 14-8-6
# create by: snower

import socket
import threading
from .protocol.result import Result

class ConnectionClosed(Exception):
    pass

class Connection(object):
    def __init__(self, host="127.0.0.1", port=5658, reader_factory = None):
        self._host = host
        self._port = port
        self._sock = None
        self._rlock = threading.Lock()
        self._wlock = threading.Lock()
        self._buffer = bytearray()
        self._reader = reader_factory(self)

    @property
    def reader(self):
        return self._reader

    def connect(self):
        err = None
        for res in socket.getaddrinfo(self._host, self._port, 0, socket.SOCK_STREAM):
            family, socktype, proto, canonname, socket_address = res
            sock = None
            try:
                sock = socket.socket(family, socktype, proto)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.connect(socket_address)
                self._sock = sock
                return
            except socket.error as _:
                err = _
                if sock is not None:
                    sock.close()

        if err is not None:
            raise err
        raise socket.error("socket.getaddrinfo returned an empty list")

    def reconnect(self):
        self.connect()

    def close(self):
        if not self._sock:
            return

        with self._wlock:
            self._sock.close()
            self._sock = None

    def write(self, command):
        command = command.dumps()
        with self._wlock:
            if not self._sock:
                self.connect()
            self._sock.sendall(command)

    def read(self):
        with self._rlock:
            if not self._sock:
                with self._wlock:
                    if not self._sock:
                        self.connect()

            try:
                data = self._sock.recv(64)
            except Exception as e:
                self.close()
                raise e

            if not data:
                self.close()
                raise ConnectionClosed()

            self._buffer += data
            if len(self._buffer) >= 64:
                data, self._buffer = self._buffer[:64], self._buffer[64:]
                result = Result(bytes(data))
                return result
            return None