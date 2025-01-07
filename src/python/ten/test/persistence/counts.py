from ten.test.persistence import normalise


class CountsPersistence:
    """Abstracts the persistence of transaction counts across accounts into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS counts " \
                 "(host VARCHAR(64), " \
                 "name VARCHAR(64), " \
                 "address VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "time INTEGER, " \
                 "count INTEGER, " \
                 "PRIMARY KEY (host, name, environment, time))"
    SQL_INSERT = "INSERT INTO counts VALUES (?, ?, ?, ?, ?, ?)"
    SQL_DELETE = "DELETE from counts WHERE host=? AND environment=?"
    SQL_SELTHR = "SELECT time, count FROM counts WHERE host=? AND name=? and environment=? ORDER BY time DESC LIMIT 3"
    SQL_SELHOR = "SELECT time, count FROM counts WHERE host=? AND name=? and environment=? and time >= ? ORDER BY time DESC"

    @classmethod
    def init(cls, host, dbconnection):
        instance = CountsPersistence(host, dbconnection)
        instance.create()
        return instance

    def __init__(self, host, dbconnection):
        """Instantiate an instance."""
        self.host = host
        self.dbconnection = dbconnection
        self.sqlins = normalise(self.SQL_INSERT, dbconnection.type)
        self.sqldel = normalise(self.SQL_DELETE, dbconnection.type)
        self.sqlthr = normalise(self.SQL_SELTHR, dbconnection.type)
        self.sqlhor = normalise(self.SQL_SELHOR, dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()

    def delete_environment(self, environment):
        """Delete all stored contract details for a particular environment."""
        self.cursor.execute(self.sqldel, (self.host, environment))
        self.dbconnection.connection.commit()

    def insert_count(self, name, address, environment, time, count):
        """Insert a new counts entry for a particular logical account."""
        self.cursor.execute(self.sqlins, (self.host, name, address, environment, time, str(count)))
        self.dbconnection.connection.commit()

    def get_last_three_counts(self, name, environment):
        """Return the transaction count with time for a particular logical account."""
        self.cursor.execute(self.sqlthr, (self.host, name, environment))
        return self.cursor.fetchall()

    def get_last_hour(self, name, environment, time):
        """Return the transaction count with time for a particular logical account."""
        self.cursor.execute(self.sqlhor, (self.host, name, environment, time))
        return self.cursor.fetchall()