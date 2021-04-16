import pymysql as DBAdapter
import sys, os

class Connection:
    def __init__(self, usr, pwd, host, port, database):
        self.db = DBAdapter.connect( host = host, user = usr,
                 password = pwd, database = database, port = int(port) )
        # self.db = DBAdapter.connect( "localhost", "root", "", "silcon" )

    def set( self, sql ):
        with self.db.cursor() as c:
            try:
                c.execute( sql )
                self.db.commit()
                return True
            except DBAdapter.err.IntegrityError:
                return -2
            except Exception as e:
                self.db.rollback()
                raise e
        return False
    
    def get( self, sql ):
        with self.db.cursor()as c:
            try:
                c.execute( sql )
                res = c.fetchall()
                return res
            except Exception as e:
                raise e
        return ()
    def getone(self, sql):
        with self.db.cursor() as c:
            try:
                c.execute(sql)
                res = c.fetchone()
                return res
            except Exception as e:
                raise e
        return ()
    def check( self, sql ):
        with self.db.cursor()as c:
            try:
                c.execute( sql )
                res = c.fetchall()
                return True if len(res) > 0 else False
            except Exception as e:
                raise e
        return False