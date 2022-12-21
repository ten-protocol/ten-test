import sqlite3, os
from pysys.constants import PROJECT


class NoncePersistence:
    SQL_CREATE = "CREATE TABLE IF NOT EXISTS nonce_db (account TEXT, environment TEXT, nonce INTEGER, status STRING)"
    SQL_INSERT = "INSERT INTO nonce_db VALUES (?, ?, ?, ?)"
    SQL_UPDATE = "UPDATE nonce_db SET status=? WHERE account=? AND environment=? AND nonce=?"
    SQL_DELETE = "DELETE * from nonce_db WHERE account=? AND environment=?"
    SQL_LATEST = "SELECT nonce FROM nonce_db WHERE account=? AND environment=? ORDER BY nonce DESC LIMIT 1"

    def __init__(self):
        self.db_dir = os.path.join(PROJECT.root, '.db')
        if not os.path.exists(self.db_dir): os.makedirs(self.db_dir)
        self.db = os.path.join(self.db_dir, 'nonce.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.SQL_CREATE)

    def insert(self, account, environment, nonce):
        self.cursor.execute(self.SQL_INSERT, (account, environment, nonce, 'PENDING'))
        self.connection.commit()

    def update(self, account, environment, nonce, status):
        self.cursor.execute(self.SQL_UPDATE, (status, account, environment, nonce))
        self.connection.commit()

    def delete(self, account, environment, nonce, status):
        self.cursor.execute(self.SQL_DELETE, (status, account, environment, nonce))
        self.connection.commit()

    def get_nonce(self, account, environment):
        self.cursor.execute(self.SQL_LATEST, (account, environment))
        try:
            result = self.cursor.fetchone()[0]
            return int(result)
        except:
            return 0
