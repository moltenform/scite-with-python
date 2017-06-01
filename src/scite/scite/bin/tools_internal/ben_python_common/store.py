# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.
# store.py, a simple database abstraction layer
#
# raison d'etre
# 1) store.py should be roughly as simple as using plain pickle/jsonpickle, but scaling better
# 2) store.py should handle common tasks like checking latest schema
# 3) store.py should avoid pysqlite's unexpected transaction semantics
# 4) eventually, store.py can be an abstract layer supporting different backends

# to install apsw, run
# python -m pip install --user
# https://github.com/rogerbinns/apsw/releases/download/3.16.2-r1/apsw-3.16.2-r1.zip
# --global-option=fetch --global-option=--version --global-option=3.16.2 --global-option=--all
# --global-option=build --global-option=--enable-all-extensions

from .common_util import *
from . import files
import apsw
import sys

class StoreException(Exception):
    def __str__(self):
        return 'StoreException: ' + Exception.__str__(self)

class Store(object):
    conn = None
    
    def add_schema(self, cursor):
        raise NotImplementedError('please inherit from Store and implement this method')
    
    def currrent_schema_version_number(self):
        raise NotImplementedError('please inherit from Store and implement this method')
    
    def stamp_schema_version(self, cursor):
        if self.currrent_schema_version_number() is None:
            return
        
        cursor.execute('CREATE TABLE ben_python_common_store_properties(schema_version INT)')
        cursor.execute('INSERT INTO ben_python_common_store_properties(schema_version) VALUES(?)',
            [self.currrent_schema_version_number()])
    
    def verify_schema_version(self):
        if self.currrent_schema_version_number() is None:
            return
        
        cursor = self.conn.cursor()
        try:
            valid = False
            got = None
            for version in cursor.execute('SELECT schema_version FROM ben_python_common_store_properties'):
                got = int(version[0])
                if got == int(self.currrent_schema_version_number()):
                    valid = True
            
            if not valid:
                raise StoreException('DB is empty or comes from a different version. Expected schema version %s, got %s' %
                    (int(self.currrent_schema_version_number()), got))
        except:
            if 'SQLError: no such table:' in str(sys.exc_info()[1]):
                raise StoreException(
                    '\n\nSchema version table not found, maybe this is a 0kb empty db. Please delete the db and try again.')
            else:
                raise
        
    def cursor(self):
        return self.conn.cursor()
    
    def row_exists(self, cursor, *args):
        for row in cursor.execute(*args):
            return True
        return False
    
    def connect_or_create(self, dbpath, flags=None):
        if flags is None:
            flags = apsw.SQLITE_OPEN_NOMUTEX | apsw.SQLITE_OPEN_READWRITE | apsw.SQLITE_OPEN_CREATE
        did_exist = files.isfile(dbpath)
        self.conn = apsw.Connection(dbpath, flags=flags)
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA temp_store = memory')
        cursor.execute('PRAGMA page_size = 16384')
        cursor.execute('PRAGMA cache_size = 1000')
        if not did_exist:
            # begin and commit a transaction
            with self:
                cursor = self.conn.cursor()
                self.add_schema(cursor)
                self.stamp_schema_version(cursor)
        
        self.verify_schema_version()
            
    def txn_begin(self):
        self.cursor().execute('BEGIN TRANSACTION')
    
    def txn_rollback(self):
        self.cursor().execute('ROLLBACK TRANSACTION')
    
    def txn_commit(self):
        self.cursor().execute('COMMIT TRANSACTION')
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        # begin txn
        self.conn.__enter__()
        return self
    
    def __exit__(self, *args):
        # rollback if exception occurred, otherwise commit
        self.conn.__exit__(*args)
