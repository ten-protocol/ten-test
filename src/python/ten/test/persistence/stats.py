from ten.test.persistence import normalise
from ten.test.persistence import get_connection


class StatsPersistence:
    """Abstracts the persistence of network statistics into a local or remote database.

    Since this is an absolute property, not one of the test runner, it should be sharable across different test runners
    when running in the cloud, so the persistence is externalised into a mysql server under these conditions.
    """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS stats " \
                 "(environment VARCHAR(64), " \
                 "time INTEGER, " \
                 "key STRING", \
                 "value INTEGER, " \
                 "delta INTEGER, " \
                 "cumulative INTEGER)"
    SQL_INSERT = "INSERT INTO stats VALUES (?, ?, ?, ?, ?, ?);"

    @classmethod
    def init(cls, use_remote, user_dir, host):
        instance = StatsPersistence(use_remote, user_dir, host)
        instance.create()
        return instance

    def __init__(self, use_remote, user_dir, host):
        """Instantiate an instance."""
        self.host = host
        self.dbconnection = get_connection(use_remote, user_dir, 'ten-test.db')
        self.sqlins = normalise(self.SQL_INSERT, self.dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()
        self.dbconnection.connection.close()

    def insert(self, environment, time, key, value, delta, cumulative):
        """Insert new values for a particular environment."""
        self.cursor.execute(self.sqlins, (environment, time, key, value, delta, cumulative))
        self.dbconnection.connection.commit()

