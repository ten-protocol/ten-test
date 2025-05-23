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
                 "type STRING, " \
                 "value INTEGER, " \
                 "delta INTEGER, " \
                 "running INTEGER)"
    SQL_INSERT = "INSERT INTO stats VALUES (?, ?, ?, ?, ?, ?);"
    SQL_SELONE = "SELECT value, running from stats WHERE environment=? and type=? order by time desc limit 1"

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
        self.sqlone = normalise(self.SQL_SELONE, self.dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()
        self.dbconnection.connection.close()

    def insert(self, environment, time, type, value, delta, running):
        """Insert new values for a particular environment."""
        self.cursor.execute(self.sqlins, (environment, time, type, value, delta, running))
        self.dbconnection.connection.commit()

    def get_last_entry(self, environment, type):
        """Return the last entry for a particular environment and type. """
        self.cursor.execute(self.sqlone, (environment, type))
        try: return self.cursor.fetchone()
        except: return None