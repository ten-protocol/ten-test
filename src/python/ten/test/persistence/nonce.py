from ten.test.persistence import normalise


class NoncePersistence:
    """Abstracts the persistence of nonces into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS nonces " \
                 "(account VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "nonce INTEGER, " \
                 "status VARCHAR(64))"
    SQL_INSERT = "INSERT INTO nonces VALUES (?, ?, ?, ?)"
    SQL_UPDATE = "UPDATE nonces SET status=? WHERE account=? AND environment=? AND nonce=?"
    SQL_DELETE = "DELETE from nonces WHERE account=? AND environment=?"
    SQL_DELFRO = "DELETE from nonces WHERE account=? AND environment=? AND nonce>=?"
    SQL_LATEST = "SELECT nonce FROM nonces WHERE account=? AND environment=? ORDER BY nonce DESC LIMIT 1"
    SQL_DELENV = "DELETE from nonces WHERE environment=?"
    SQL_ACCNTS = "SELECT DISTINCT account from nonces WHERE environment=?"
    SQL_DELENT = "DELETE from nonces WHERE account=? AND environment=? AND nonce=?"

    @classmethod
    def init(cls, host, dbconnection):
        instance = NoncePersistence(host, dbconnection)
        instance.create()
        return instance

    def __init__(self, host, dbconnection):
        """Instantiate an instance."""
        self.host = host
        self.dbconnection = dbconnection
        self.sqlins = normalise(self.SQL_INSERT, dbconnection.type)
        self.sqlupd = normalise(self.SQL_UPDATE, dbconnection.type)
        self.sqldel = normalise(self.SQL_DELETE, dbconnection.type)
        self.delfro = normalise(self.SQL_DELFRO, dbconnection.type)
        self.latest = normalise(self.SQL_LATEST, dbconnection.type)
        self.delenv = normalise(self.SQL_DELENV, dbconnection.type)
        self.accnts = normalise(self.SQL_ACCNTS, dbconnection.type)
        self.delent = normalise(self.SQL_DELENT, dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence. """
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence. """
        self.cursor.close()

    def get_next_nonce(self, test, web3, account, environment, persist_nonce=True, log=True):
        """Get the next nonce to use in a transaction.

        If persist_nonce is false then the return value will be the transaction count as received from the network.
        Otherwise, this method will look up the last persisted value and return the next value to use. Note that nonces
        start from zero, so if the tx count is 5 the nonces so far would have be 0,1,2,3,4. Hence the next nonce should
        always match the tx count. 
        """
        transaction_count = web3.eth.get_transaction_count(account)
        persisted_nonce = self.get_latest_nonce(account, environment)

        nonce = transaction_count
        if persist_nonce:
            nonce = 0 if persisted_nonce is None else persisted_nonce+1      # we have to believe the local store
            self.insert(account, test.env, nonce)
            if log: test.log.info("Account %s count %d using nonce from persistence as %d", account, transaction_count, nonce)
        else:
            if log: test.log.info("Account %s using nonce from transaction count as %d", account, nonce)
        return nonce

    def insert(self, account, environment, nonce, status='PENDING'):
        """Insert a new nonce into the persistence. """
        self.cursor.execute(self.sqlins, (account, environment, nonce, status))
        self.dbconnection.connection.commit()

    def update(self, account, environment, nonce, status):
        """Update the status of a transaction for a given nonce into the persistence. """
        self.cursor.execute(self.sqlupd, (status, account, environment, nonce))
        self.dbconnection.connection.commit()

    def delete(self, account, environment):
        """Delete all nonce entries in the persistence for a given account and environment. """
        self.cursor.execute(self.sqldel, (account, environment))
        self.dbconnection.connection.commit()

    def delete_from(self, account, environment, nonce):
        """Delete all nonce entries in the persistence for a given account and environment. """
        self.cursor.execute(self.delfro, (account, environment, nonce))
        self.dbconnection.connection.commit()

    def delete_environment(self, environment):
        """Delete all nonce entries for all accounts for a given environment. """
        self.cursor.execute(self.delenv, (environment, ))
        self.dbconnection.connection.commit()

    def delete_entries(self, account, environment, nonce):
        """Delete all nonce entries in the persistence for a given account and environment and nonce. """
        self.cursor.execute(self.delent, (account, environment, nonce))
        self.dbconnection.connection.commit()

    def get_accounts(self, environment):
        """Return a list of all accounts with persisted values for a given environment. """
        self.cursor.execute(self.accnts, (environment))
        return self.cursor.fetchall()

    def get_latest_nonce(self, account, environment):
        """Get the latest nonce for a given account and environment. """
        self.cursor.execute(self.latest, (account, environment))
        try:
            result = self.cursor.fetchone()[0]
            return int(result)
        except:
            return None
