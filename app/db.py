import os
from psycopg2 import pool, DatabaseError


class DBPool(object):

    def __init__(self, min_conns=None, max_conns=None, database=None, username=None, password=None, host=None, port=None):
        min_conns = min_conns or os.environ.get('DB_MIN_CONNS')
        max_conns = max_conns or os.environ.get('DB_MAX_CONNS')
        database = database or os.environ.get('DB_DATABASE')
        username = username or os.environ.get('DB_USERNAME')
        password = password or os.environ.get('DB_PASSWORD')
        host = host or os.environ.get('DB_HOST')
        port = port or os.environ.get('DB_PORT')
        self.pool = pool.ThreadedConnectionPool(
            min_conns,
            max_conns,
            database=database,
            user=username,
            password=password,
            host=host,
            port=port
        )
        if not self.pool:
            raise DatabaseError("Failed to create database pool")

    def getconn(self):
        return self.pool.getconn()

    def putconn(self, conn):
        self.pool.putconn(conn)

    def close(self):
        self.pool.closeall()

    def __del__(self):
        self.close()
        self.pool = None

