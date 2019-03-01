# -*- coding: utf-8 -*-
# 18/7/30
# create by: snower

import threading
from collections import deque
from .connection import Connection as BaseConnection

class Connection(BaseConnection):
    def __init__(self, pool, *args, **kwargs):
        self._pool = pool
        super(Connection, self).__init__(*args, **kwargs)

    def close(self):
        self._pool.release_connection(self)

class ConnectionPool(object):
    def __init__(self, host="127.0.0.1", port=5658, max_conntion = 4, reader_factory = None):
        self._host = host
        self._port = port
        self._max_conntion = max_conntion
        self._connections = deque()
        self._used_conntions = {}
        self._lock = threading.Lock()
        self._semaphore = threading.Semaphore(self._max_conntion)
        self._reader_factory = reader_factory

    def create_connection(self):
        conn = Connection(self, self._host, self._port, self._reader_factory)
        conn.reader.start()
        self._connections.append(conn)
        return conn

    def get_connection(self):
        self._semaphore.acquire(True)
        try:
            with self._lock:
                if self._connections:
                    conn = self._connections.popleft()
                    self._used_conntions[id(conn)] = conn
                    return conn

                conn = self.create_connection()
                self._used_conntions[id(conn)] = conn
                return conn
        except Exception as e:
            self._semaphore.release()
            raise e

    def release_connection(self, conn):
        with self._lock:
            if id(conn) in self._used_conntions:
                del self._used_conntions[id(conn)]
                self._connections.append(conn)
                self._semaphore.release()

    def close(self):
        with self._lock:
            while self._connections:
                conn = self._connections.popleft()
                conn.close()

            for conn_id, conn in self._used_conntions:
                conn.close()
            self._used_conntions = {}