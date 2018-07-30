# -*- coding: utf-8 -*-
# 18/7/30
# create by: snower

import threading

class Reader(object):
    def __init__(self, connection):
        self._connection = connection
        self._client = None
        self._reader_thread = None
        self._is_stop = False

    @property
    def is_running(self):
        return self._reader_thread is not None

    def set_client(self, client):
        self._client = client

    def run(self):
        while not self._is_stop:
            try:
                result = self._connection.read()
            except:
                self._connection.close()
                self._connection.reconnect()
                continue

            try:
                if result:
                    self._client.on_result(result)
            except:
                pass

        self._connection = None
        self._client = None

    def start(self):
        self._reader_thread = threading.Thread()
        self._reader_thread.setDaemon(True)
        self._reader_thread.start()

    def stop(self):
        self._is_stop = True
        self._connection.close()