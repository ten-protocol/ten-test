from ten.test.persistence import normalise

class FundsPersistence:
    """Abstracts the persistence of funds across accounts into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS funds " \
                 "(name VARCHAR(64), " \
                 "address VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "time INTEGER, " \
                 "balance INTEGER, " \
                 "PRIMARY KEY (name, environment, time))"
    SQL_INSERT = "INSERT INTO funds VALUES (?, ?, ?, ?, ?)"
    SQL_DELETE = "DELETE from funds WHERE environment=?"
    SQL_SELECT = "SELECT time, balance FROM funds WHERE name=? and environment=? ORDER BY time DESC"

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

    def delete_environment(self, environment):
        """Delete all stored details for a particular environment."""
        self.cursor.execute(self.delete, (environment, ))
        self.dbconnection.connection.commit()

    def insert_funds(self, name, address, environment, time, balance):
        """Insert a new funds entry for a particular logical account."""
        self.cursor.execute(self.insert, (name, address, environment, time, str(balance)))
        self.dbconnection.connection.commit()

    def get_funds(self, name, environment):
        """Return the funds with time for a particular logical account."""
        self.cursor.execute(self.select, (name, environment))
        return self.cursor.fetchall()

