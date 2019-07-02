#!/usr/bin/env python
import sqlite3
from urllib.request import pathname2url

class DBConnect:
    def __init__(self, name):
       self.name = name
       self.db_conn = None

    def __enter__(self):
        try:
            dbURI = 'file:{}?mode=rw'.format(pathname2url(self.name))
            self.db_conn = sqlite3.connect(dbURI, uri=True)
            return self.db_conn
        except sqlite3.OperationalError as e:
            print(e, ":", CARD_DB)
            raise e
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_conn.close()
