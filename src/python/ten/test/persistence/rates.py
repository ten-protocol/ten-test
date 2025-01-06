from ten.test.persistence import normalise


class RatesPersistence:
    """Abstracts the persistence of rates across cryptos into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS rates " \
                 "(crypto VARCHAR(3), " \
                 "currency VARCHAR(3), " \
                 "time INTEGER, " \
                 "rate VARCHAR(255), " \
                 "PRIMARY KEY (crypto, currency, time))"
    SQL_INSERT = "INSERT INTO rates VALUES (?, ?, ?, ?);"
    SQL_DELETE = "DELETE from rates WHERE crypto=?;"
    SQL_SELECT = "SELECT time, rate FROM rates WHERE crypto=? and currency=? ORDER BY time DESC LIMIT 1;"

    def __init__(self, dbconnection):
        """Instantiate an instance."""
        self.dbconnection = dbconnection
        self.insert = normalise(self.SQL_INSERT, dbconnection.type)
        self.delete = normalise(self.SQL_DELETE, dbconnection.type)
        self.select = normalise(self.SQL_SELECT, dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()

    def delete_crypto(self, crypto):
        """Delete all stored rates for a particular crypto."""
        self.cursor.execute(self.delete, (crypto, ))
        self.dbconnection.connection.commit()

    def insert_rates(self, crypto, currency, time, rate):
        """Insert a new rate for a particular crypto and currency."""
        self.cursor.execute(self.insert, (crypto, currency, time, str(rate)))
        self.dbconnection.connection.commit()

    def get_latest_rate(self, crypto, currency):
        """Return the latest rate for the crypto and currency."""
        self.cursor.execute(self.select, (crypto, currency))
        try:
            result = self.cursor.fetchone()[1]
            return float(result)
        except:
            return None




