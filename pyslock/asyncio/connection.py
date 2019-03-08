# -*- coding: utf-8 -*-
# 18/8/3
# create by: snower

from __future__ import absolute_import, division, print_function

from asyncio import coroutine, events, Protocol, ensure_future
from ..protocol.result import Result
from ..protocol.exceptions import ConnectTimeOutError


class Connection(Protocol):
    def __init__(self, client, host="127.0.0.1", port=5658):
        self._client = client
        self._host = host
        self._port = port
        self._wbuffer = []
        self._rbuffer = bytearray()
        self._rbuffer_size = 0
        self._stream = None
        self._loop_connect_timeout = None
        self._connecting = False
        self._connected = False
        self._transport = None

    def on_close(self):
        self._connected = False
        self._client.on_connection_close()

    @coroutine
    def _connect(self, address):
        if isinstance(address, (str, bytes)):
            self._transport, _ = yield from self._loop.create_unix_connection(lambda : self, address)
        else:
            self._transport, _ = yield from self._loop.create_connection(lambda : self, address[0], address[1])

    def connect(self):
        self._loop = events.get_event_loop()

        def connected(connect_future):
            if self._loop_connect_timeout:
                self._loop_connect_timeout.cancel()
                self._loop_connect_timeout = None

            try:
                self._stream = connect_future.result()
                self._connected = True

                for command, future in self._wbuffer:
                    self.write(command, future)
                self._wbuffer = []
            except:
                self.on_close()
            self._connecting = False

        self._connecting = True
        connect_future = ensure_future(self._connect((self._host, self._port)))
        connect_future.add_done_callback(connected)

        def timeout():
            if not self._connected:
                for command, future in self._wbuffer:
                    future.set_exception(ConnectTimeOutError())
                self._wbuffer = []
                self._transport = None
                self._stream = None
                self._connecting = False
            self._loop_connect_timeout = None

        self._loop_connect_timeout = self._loop.call_later(5, timeout)

    def connection_made(self, transport):
        self._transport = transport
        if self._connected:
            transport.close()
        else:
            self._transport.set_write_buffer_limits(1024 * 1024 * 1024)

    def data_received(self, data):
        self._rbuffer += data
        self._rbuffer_size += len(data)

        while self._rbuffer_size >= 64:
            data, self._rbuffer = self._rbuffer[:64], self._rbuffer[64:]
            self._rbuffer_size -= 64
            result = Result(bytes(data))
            self._client.on_result(result)

    def connection_lost(self, exc):
        self.on_close()
        self._transport = None
        self._stream = None

    def eof_received(self):
        return False

    def write(self, command, future):
        if not self._connected:
            if not self._connecting:
                self.connect()
            self._wbuffer.append((command, future))
        else:
            try:
                command = command.dumps()
                command += (64 - len(command)) * b'\x00'
                self._transport.write(command)
            except Exception as e:
                future.set_exception(e)

    def close(self):
        if not self._connected:
            return

        if self._transport:
            self._transport.close()
        else:
            self.on_close()