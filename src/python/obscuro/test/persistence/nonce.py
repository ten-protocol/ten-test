import sqlite3, os


class NoncePersistence:
    """Abstracts the persistence of nonces into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS nonce_db (account TEXT, environment TEXT, nonce INTEGER, status STRING)"
    SQL_INSERT = "INSERT INTO nonce_db VALUES (?, ?, ?, ?)"
    SQL_UPDATE = "UPDATE nonce_db SET status=? WHERE account=? AND environment=? AND nonce=?"
    SQL_DELETE = "DELETE from nonce_db WHERE account=? AND environment=?"
    SQL_LATEST = "SELECT nonce FROM nonce_db WHERE account=? AND environment=? ORDER BY nonce DESC LIMIT 1"
    SQL_DELENV = "DELETE from nonce_db WHERE environment=?"
    SQL_ACCNTS = "SELECT DISTINCT account from nonce_db where environment=?"

    def __init__(self, db_dir):
        """Instantiate an instance. """
        self.db = os.path.join(db_dir, 'nonce.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence. """
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence. """
        self.connection.close()

    def get_next_nonce(self, test, web3, account, environment, persist_nonce=True, log=True):
        """Get the next nonce to use in a transaction.

        If persist_nonce is false then the return value will be the transaction count as received from the network.
        Otherwise, this method will look up the last persisted value and return the next value to use. Note that the
        method performs some logic around persistence reset i.e. if the transaction count is zero it assumes a new
        network has been deployed and clears the persistence for that account.
        """
        transaction_count = web3.eth.get_transaction_count(account)
        persisted_nonce = self.get_latest_nonce(account, environment)

        nonce = transaction_count
        if persist_nonce:
            if transaction_count == 0:                                                         # implies a new testnet deployment
                if log: test.log.info('Clearing nonce_db for %s on zero tx count' % account)   # so clear out the persistence
                self.delete(account, environment)
            else:
                nonce = 0 if persisted_nonce is None else persisted_nonce+1      # we have to believe the local store
            test.nonce_db.insert(account, test.env, nonce)
            if log: test.log.info("Account %s count %d using nonce from persistence as %d" % (account, transaction_count, nonce))
        else:
            if log: test.log.info("Account %s using nonce from transaction count as %d" % (account, nonce))
        return nonce

    def insert(self, account, environment, nonce, status='PENDING'):
        """Insert a new nonce into the persistence. """
        self.cursor.execute(self.SQL_INSERT, (account, environment, nonce, status))
        self.connection.commit()

    def update(self, account, environment, nonce, status):
        """Update the statuus of a transaction for a given nonce into the persistence. """
        self.cursor.execute(self.SQL_UPDATE, (status, account, environment, nonce))
        self.connection.commit()

    def delete(self, account, environment):
        """Delete all nonce entries in the persistence for a given account and environment. """
        self.cursor.execute(self.SQL_DELETE, (account, environment))
        self.connection.commit()

    def delete_environment(self, environment):
        """Delete all nonce entries for all accounts for a given environment. """
        self.cursor.execute(self.SQL_DELENV, (environment, ))
        self.connection.commit()

    def get_accounts(self, environment):
        """Return a list of all accounts with persisted values for a given environment. """
        self.cursor.execute(self.SQL_ACCNTS, (environment, ))
        return self.cursor.fetchall()

    def get_latest_nonce(self, account, environment):
        """Get the latest nonce for a given account and environment. """
        self.cursor.execute(self.SQL_LATEST, (account, environment))
        try:
            result = self.cursor.fetchone()[0]
            return int(result)
        except:
            return None
