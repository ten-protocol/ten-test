class RatesPersistence:
    """Abstracts the persistence of rates across cryptos into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS rates " \
                 "(crypto TEXT, currency INTEGER, time INTEGER, rate TEXT, " \
                 "PRIMARY KEY (crypto, currency, time))"
    SQL_INSERT = "INSERT INTO rates VALUES (?, ?, ?, ?)"
    SQL_DELETE = "DELETE from rates WHERE crypto=?"
    SQL_SELECT = "SELECT time, rate FROM rates WHERE crypto=? and currency=? ORDER BY time DESC LIMIT 1"

    def __init__(self, connection):
        """Instantiate an instance."""
        self.connection = connection
        self.cursor = self.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()

    def delete_crypto(self, crypto):
        """Delete all stored rates for a particular crypto."""
        self.cursor.execute(self.SQL_DELETE, (crypto, ))
        self.connection.commit()

    def insert_rates(self, crypto, currency, time, rate):
        """Insert a new rate for a particular crypto and currency."""
        self.cursor.execute(self.SQL_INSERT, (crypto, currency, time, str(rate)))
        self.connection.commit()

    def get_latest_rate(self, crypto, currency):
        """Return the latest rate for the crypto and currency."""
        self.cursor.execute(self.SQL_SELECT, (crypto, currency))
        try:
            result = self.cursor.fetchone()[1]
            return float(result)
        except:
            return None


