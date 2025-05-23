from ten.test.persistence import normalise
from ten.test.persistence import get_connection


class CountsPersistence:
    """Abstracts the persistence of transaction counts across accounts into a local or remote database.

    This is only really used to persist the tx count of the L1 sequencer, as it means we can ensure that it is writing
    roll-ups to the L1. Since this is a property of the environment, not the test runner, it should be sharable across
    different test runners when running in the cloud, so the persistence is externalised into a mysql server under these
    conditions.
    """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS counts " \
                 "(name VARCHAR(64), " \
                 "address VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "time INTEGER, " \
                 "count INTEGER, " \
                 "PRIMARY KEY (name, environment, time))"
    SQL_INSERT = "INSERT INTO counts VALUES (?, ?, ?, ?, ?)"
    SQL_DELETE = "DELETE from counts WHERE environment=?"
    SQL_SELTHR = "SELECT time, count FROM counts WHERE name=? AND address = ? AND environment=? ORDER BY time DESC LIMIT 3"
    SQL_SELHOR = "SELECT time, count FROM counts WHERE name=? AND address = ? AND environment=? and time >= ? ORDER BY time DESC"

    @classmethod
    def init(cls, use_remote, user_dir, host):
        instance = CountsPersistence(use_remote, user_dir, host)
        instance.create()
        return instance

    def __init__(self, use_remote, user_dir, host):
        """Instantiate an instance."""
        self.host = host
        self.dbconnection = get_connection(use_remote, user_dir, 'ten-test.db')
        self.sqlins = normalise(self.SQL_INSERT, self.dbconnection.type)
        self.sqldel = normalise(self.SQL_DELETE, self.dbconnection.type)
        self.sqlthr = normalise(self.SQL_SELTHR, self.dbconnection.type)
        self.sqlhor = normalise(self.SQL_SELHOR, self.dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()
        self.dbconnection.connection.close()

    def delete_environment(self, environment):
        """Delete all stored contract details for a particular environment."""
        self.cursor.execute(self.sqldel, (environment,))
        self.dbconnection.connection.commit()

    def insert_count(self, name, address, environment, time, count):
        """Insert a new counts entry for a particular logical account."""
        self.cursor.execute(self.sqlins, (name, address, environment, time, str(count)))
        self.dbconnection.connection.commit()

    def get_last_three_counts(self, name, address, environment):
        """Return the transaction count with time for a particular logical account."""
        self.cursor.execute(self.sqlthr, (name, address, environment))
        return self.cursor.fetchall()

    def get_since_time(self, name, address, environment, time):
        """Return the transaction count with time for a particular logical account."""
        self.cursor.execute(self.sqlhor, (name, address, environment, time))
        return self.cursor.fetchall()