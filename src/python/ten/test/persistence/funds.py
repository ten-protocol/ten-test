from ten.test.persistence import normalise
from ten.test.persistence import get_connection


class FundsPersistence:
    """Abstracts the persistence of funds across accounts into a local database.

    Since this is a property of the environment, not the test runner, it should be sharable across different test
    runners when running in the cloud, so the persistence is externalised into a mysql server under these conditions.
    """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS funds " \
                 "(name VARCHAR(64), " \
                 "address VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "time INTEGER, " \
                 "balance VARCHAR(64), " \
                 "PRIMARY KEY (name, environment, time))"
    SQL_INSERT = "INSERT INTO funds VALUES (?, ?, ?, ?, ?)"
    SQL_DELETE = "DELETE from funds WHERE environment=?"
    SQL_SELECT = "SELECT time, balance FROM funds WHERE name=? and environment=? ORDER BY time DESC"

    @classmethod
    def init(cls, is_local_ten, user_dir, host=None, is_cloud=None):
        instance = FundsPersistence(is_local_ten, user_dir, host, is_cloud)
        instance.create()
        return instance

    def __init__(self, is_local_ten, user_dir, host=None, is_cloud=None):
        """Instantiate an instance."""
        self.host = host
        self.dbconnection = get_connection(is_local_ten, is_cloud, user_dir, 'ten-test.db')
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

    def delete_environment(self, environment):
        """Delete all stored details for a particular environment."""
        self.cursor.execute(self.sqldel, (environment, ))
        self.dbconnection.connection.commit()

    def insert_funds(self, name, address, environment, time, balance):
        """Insert a new funds entry for a particular logical account."""
        self.cursor.execute(self.sqlins, (name, address, environment, time, str(balance)))
        self.dbconnection.connection.commit()

    def get_funds(self, name, environment):
        """Return the funds with time for a particular logical account."""
        self.cursor.execute(self.sqlsel, (name, environment))
        return self.cursor.fetchall()

