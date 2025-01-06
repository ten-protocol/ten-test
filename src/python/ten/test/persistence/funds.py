class FundsPersistence:
    """Abstracts the persistence of funds across accounts into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS funds " \
                 "(name TEXT, address INTEGER, environment TEXT, time INTEGER, balance TEXT, " \
                 "PRIMARY KEY (name, environment, time))"
    SQL_INSERT = "INSERT INTO funds VALUES (?, ?, ?, ?, ?)"
    SQL_DELETE = "DELETE from funds WHERE environment=?"
    SQL_SELECT = "SELECT time, balance FROM funds WHERE name=? and environment=? ORDER BY time DESC"

    def __init__(self, dbconnection):
        """Instantiate an instance."""
        self.dbconnection = dbconnection
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()

    def delete_environment(self, environment):
        """Delete all stored details for a particular environment."""
        self.cursor.execute(self.SQL_DELETE, (environment, ))
        self.dbconnection.connection.commit()

    def insert_funds(self, name, address, environment, time, balance):
        """Insert a new funds entry for a particular logical account."""
        self.cursor.execute(self.SQL_INSERT, (name, address, environment, time, str(balance)))
        self.dbconnection.connection.commit()

    def get_funds(self, name, environment):
        """Return the funds with time for a particular logical account."""
        self.cursor.execute(self.SQL_SELECT, (name, environment))
        return self.cursor.fetchall()

