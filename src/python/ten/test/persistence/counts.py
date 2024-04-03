import sqlite3, os


class CountsPersistence:
    """Abstracts the persistence of transaction counts across accounts into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS counts " \
                 "(name TEXT, address INTEGER, environment TEXT, time INTEGER, count TEXT, " \
                 "PRIMARY KEY (name, environment, time))"
    SQL_INSERT = "INSERT INTO counts VALUES (?, ?, ?, ?, ?)"
    SQL_DELETE = "DELETE from counts WHERE environment=?"
    SQL_SELECT_THREE = "SELECT time, count FROM counts WHERE name=? and environment=? ORDER BY time DESC LIMIT 3"
    SQL_SELECT_HOUR = "SELECT time, count FROM counts WHERE name=? and environment=? and time >= ? ORDER BY time DESC"

    def __init__(self, db_dir):
        """Instantiate an instance."""
        self.db = os.path.join(db_dir, 'counts.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.connection.close()

    def delete_environment(self, environment):
        """Delete all stored contract details for a particular environment."""
        self.cursor.execute(self.SQL_DELETE, (environment, ))
        self.connection.commit()

    def insert_count(self, name, address, environment, time, count):
        """Insert a new counts entry for a particular logical account."""
        self.cursor.execute(self.SQL_INSERT, (name, address, environment, time, str(count)))
        self.connection.commit()

    def get_last_three_counts(self, name, environment):
        """Return the transaction count with time for a particular logical account."""
        self.cursor.execute(self.SQL_SELECT_THREE, (name, environment))
        return self.cursor.fetchall()

    def get_last_hour(self, name, environment, time):
        """Return the transaction count with time for a particular logical account."""
        self.cursor.execute(self.SQL_SELECT_HOUR, (name, environment))
        return self.cursor.fetchall()