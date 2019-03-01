# -*- coding: utf-8 -*-
# 18/7/30
# create by: snower

import time
import threading

class Reader(object):
    def __init__(self, client, connection):
        self._connection = connection
        self._client = client
        self._reader_thread = None
        self._is_stop = False

    @property
    def is_running(self):
        return self._reader_thread is not None

    def run(self):
        while not self._is_stop:
            try:
                result = self._connection.read()
            except:
                try:
                    self._connection.close()
                    time.sleep(2)
                    self._connection.reconnect()
                except:
                    pass
                continue

            try:
                if result:
                    self._client.on_result(result)
            except:
                pass

        self._connection = None
        self._client = None

    def start(self):
        self._reader_thread = threading.Thread(target=self.run)
        self._reader_thread.setDaemon(True)
        self._reader_thread.start()

    def stop(self):
        self._is_stop = True
        self._connection.close()