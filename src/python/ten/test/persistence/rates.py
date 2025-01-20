from ten.test.persistence import normalise
from ten.test.persistence import get_connection


class RatesPersistence:
    """Abstracts the persistence of rates across cryptos into a local database.

    Since this is an absolute property, not one of the test runner, it should be sharable across different test runners
    when running in the cloud, so the persistence is externalised into a mysql server under these conditions.
    """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS rates " \
                 "(crypto VARCHAR(3), " \
                 "currency VARCHAR(3), " \
                 "time INTEGER, " \
                 "rate VARCHAR(64), " \
                 "PRIMARY KEY (crypto, currency, time))"
    SQL_INSERT = "INSERT INTO rates VALUES (?, ?, ?, ?);"
    SQL_DELETE = "DELETE from rates WHERE crypto=?;"
    SQL_SELECT = "SELECT time, rate FROM rates WHERE crypto=? and currency=? ORDER BY time DESC LIMIT 1;"

    @classmethod
    def init(cls, use_remote, user_dir, host):
        instance = RatesPersistence(use_remote, user_dir, host)
        instance.create()
        return instance

    def __init__(self, use_remote, user_dir, host):
        """Instantiate an instance."""
        self.host = host
        self.dbconnection = get_connection(use_remote, user_dir, 'ten-test.db')
        self.sqlins = normalise(self.SQL_INSERT, self.dbconnection.type)
        self.sqldel = normalise(self.SQL_DELETE, self.dbconnection.type)
        self.sqlsel = normalise(self.SQL_SELECT, self.dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()
        self.dbconnection.connection.close()

    def delete_crypto(self, crypto):
        """Delete all stored rates for a particular crypto."""
        self.cursor.execute(self.sqldel, (crypto, ))
        self.dbconnection.connection.commit()

    def insert_rates(self, crypto, currency, time, rate):
        """Insert a new rate for a particular crypto and currency.

        Note rates are only inserted if they are newer than the last recorded by 1 hour.
        """
        last_time, _ = self.cursor.get_latest_rate(crypto, currency)
        if last_time is not None and time > last_time + 3600:
            try:
                self.cursor.execute(self.sqlins, (crypto, currency, time, str(rate)))
                self.dbconnection.connection.commit()
            except:
                pass # fail silently

    def get_latest_rate(self, crypto, currency):
        """Return the latest rate for the crypto and currency."""
        self.cursor.execute(self.sqlsel, (crypto, currency))
        try:
            result = self.cursor.fetchone()
            return int(result[0]), float(result[1])
        except:
            return None, None




