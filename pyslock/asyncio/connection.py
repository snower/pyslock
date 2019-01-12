# -*- coding: utf-8 -*-
# 18/8/3
# create by: snower

import time
import socket
from tornado.iostream import IOStream
from tornado.ioloop import IOLoop


class ConnectTimeOutError(Exception):
    pass


class Connection(object):
    def __init__(self, client, host="127.0.0.1", port=5658):
        self._client = client
        self._host = host
        self._port = port
        self._buffer = []
        self._stream = None
        self._connecting = False
        self._connected = False

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._stream = IOStream(s)
        self._stream.set_close_callback(self.on_close)
        self._stream.connect((self._host, self._port), self.on_connect)
        self._connecting = True

        def timeout():
            if not self._connected:
                for command, future in self._buffer:
                    future.set_exception(ConnectTimeOutError())
                self._buffer = []
                self._connecting = False
        IOLoop.current().add_timeout(time.time() + 5, timeout)

    def on_close(self):
        self._connected = False

    def write(self, command, future):
        if not self._connected:
            if not self._connecting:
                self.connect()
            self._buffer.append((command, future))
        else:
            try:
                command = command.dumps()
                command += (64 - len(command)) * b'\x00'
                self._stream.write(command)
            except Exception as e:
                future.set_exception(e)

    def on_connect(self):
        self._connected = True
        self._connecting = False
        for command, future in self._buffer:
            self.write(command, future)
        self.loop()

    def loop(self):
        def on_data(data):
            self._client.on_data(data)
            self._stream.read_bytes(64, on_data)
        self._stream.read_bytes(64, on_data)

    def close(self):
        self._stream.close()
        self._stream = None
        self._connected = False