import sqlite3, os


class NoncePersistence:
    SQL_CREATE = "CREATE TABLE IF NOT EXISTS nonce_db (account TEXT, environment TEXT, nonce INTEGER, status STRING)"
    SQL_INSERT = "INSERT INTO nonce_db VALUES (?, ?, ?, ?)"
    SQL_UPDATE = "UPDATE nonce_db SET status=? WHERE account=? AND environment=? AND nonce=?"
    SQL_DELETE = "DELETE from nonce_db WHERE account=? AND environment=?"
    SQL_LATEST = "SELECT nonce FROM nonce_db WHERE account=? AND environment=? ORDER BY nonce DESC LIMIT 1"
    SQL_DELENV = "DELETE from nonce_db WHERE environment=?"
    SQL_ACCNTS = "SELECT DISTINCT account from nonce_db where environment=?"

    def __init__(self, db_dir):
        self.db = os.path.join(db_dir, 'nonce.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def create(self):
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        self.connection.close()

    def get_next_nonce(self, test, web3, account, environment, persist_nonce=True):
        transaction_count = web3.eth.get_transaction_count(account)
        last_nonce = self.get_latest_nonce(account, environment)

        nonce = transaction_count
        if transaction_count == 0:
            self.delete(account, environment)                                 # implies a new testnet deployment
        if persist_nonce:
            nonce = 0 if last_nonce is None else last_nonce+1                 # we have to believe the local store
            test.log.info("Account %s count %d using nonce from persistence as %d" % (account, transaction_count, nonce))
        else:
            test.log.info("Account %s using nonce from transaction count as %d" % (account, nonce))
        return nonce

    def insert(self, account, environment, nonce, status='PENDING'):
        self.cursor.execute(self.SQL_INSERT, (account, environment, nonce, status))
        self.connection.commit()

    def update(self, account, environment, nonce, status):
        self.cursor.execute(self.SQL_UPDATE, (status, account, environment, nonce))
        self.connection.commit()

    def delete(self, account, environment):
        self.cursor.execute(self.SQL_DELETE, (account, environment))
        self.connection.commit()

    def delete_environment(self, environment):
        self.cursor.execute(self.SQL_DELENV, (environment, ))
        self.connection.commit()

    def get_accounts(self, environment):
        self.cursor.execute(self.SQL_ACCNTS, (environment, ))
        return self.cursor.fetchall()

    def get_latest_nonce(self, account, environment):
        self.cursor.execute(self.SQL_LATEST, (account, environment))
        try:
            result = self.cursor.fetchone()[0]
            return int(result)
        except:
            return None
