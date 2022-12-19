import sqlite3, os
from pysys.constants import PROJECT


class NoncePersistence:

    def __init__(self):
        self.db = os.path.join(PROJECT.root, '.runner', 'nonce.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS nonce_db (account TEXT, environment TEXT, nonce INTEGER, status STRING)")

    def insert(self, account, environment, nonce):
        self.cursor.execute("INSERT INTO nonce_db VALUES ('%s', '%s', %d, '%s')" % (account, environment, nonce, 'PENDING'))
        self.connection.commit()

    def update(self, account, environment, nonce, status):
        self.cursor.execute("UPDATE nonce_db SET status='%s' WHERE account='%s' AND environment='%s' AND nonce=%d" %
                            (status, account, environment, nonce))
        self.connection.commit()

    def get_nonce(self, account, environment):
        self.cursor.execute("SELECT nonce FROM nonce_db where account=%s AND environment=%s ORDER BY column DESC LIMIT 1;" %
                            (account, environment))
