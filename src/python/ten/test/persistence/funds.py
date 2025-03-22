from ten.test.persistence import normalise
from ten.test.persistence import get_connection


class GasPricePersistence:
    """Abstracts the persistence of gas prices across the l1 and l2 into a local database.

    Since this is an absolute property, not one of the test runner, it should be sharable across different test runners
    when running in the cloud, so the persistence is externalised into a mysql server under these conditions.
    """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS gas_prices " \
                 "(environment VARCHAR(64), " \
                 "time INTEGER, " \
                 "l1gasprice REAL, " \
                 "l2gasprice REAL) " \
                 "l1blobprice REAL)"
    SQL_INSERT = "INSERT INTO gas_prices VALUES (?, ?, ?, ?, ?);"

    @classmethod
    def init(cls, use_remote, user_dir, host):
        instance = GasPricePersistence(use_remote, user_dir, host)
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

    def insert(self, environment, time, l1gasprice, l2gasprice, l1blobprice):
        """Insert new values for a particular environment."""
        self.cursor.execute(self.sqlins, (environment, time, l1gasprice, l2gasprice, l1blobprice))
        self.dbconnection.connection.commit()


class PandLPersistence:
    """Abstracts the persistence of profit and loss into a local database.

    Since this is a property of the environment, not the test runner, it should be sharable across different test
    runners when running in the cloud, so the persistence is externalised into a mysql server under these conditions.
    """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS pandl " \
                 "(environment VARCHAR(64), " \
                 "time INTEGER, " \
                 "seq_diff REAL, " \
                 "gas_diff REAL, " \
                 "pandl REAL, " \
                 "PRIMARY KEY (environment, time))"
    SQL_INSERT = "INSERT INTO pandl VALUES (?, ?, ?, ?, ?)"
    SQL_DELETE = "DELETE from pandl WHERE environment=?"
    SQL_SELECT = "SELECT time, seq_diff, gas_diff, pandl FROM pandl WHERE environment=? ORDER BY time DESC"

    @classmethod
    def init(cls, use_remote, user_dir, host):
        instance = PandLPersistence(use_remote, user_dir, host)
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

    def delete_environment(self, environment):
        """Delete all stored details for a particular environment."""
        self.cursor.execute(self.sqldel, (environment, ))
        self.dbconnection.connection.commit()

    def insert_pandl(self, environment, time, seq_diff, gas_diff, pandl):
        """Insert a new pandl entry for a particular environment."""
        self.cursor.execute(self.sqlins, (environment, time, seq_diff, gas_diff, pandl))
        self.dbconnection.connection.commit()

    def get_pandl(self, environment):
        """Return the pandl with time for a particular environment."""
        self.cursor.execute(self.sqlsel, (environment))
        return self.cursor.fetchall()


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
    def init(cls, use_remote, user_dir, host):
        instance = FundsPersistence(use_remote, user_dir, host)
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

