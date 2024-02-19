import sqlite3, os


class FundsPersistence:
    """Abstracts the persistence of funds across accounts into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS funds " \
                 "(name TEXT, address INTEGER, time INTEGER, balance INTEGER, " \
                 "PRIMARY KEY name)"
    SQL_INSERT = "INSERT OR REPLACE INTO funds VALUES (?, ?, ?, ?)"
    SQL_DELETE = "DELETE from funds WHERE name=?"
    SQL_SELECT = "SELECT time, balance FROM funds WHERE name=? ORDER BY time DESC"

    def __init__(self, db_dir):
        """Instantiate an instance."""
        self.db = os.path.join(db_dir, 'funds.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.connection.close()

    def delete_name(self, name):
        """Delete all stored fund details for a particular logical account."""
        self.cursor.execute(self.SQL_DELETE, (name, ))
        self.connection.commit()

    def insert_funds(self, name, address, time, balance):
        """Insert a new funds entry for a particular logical account."""
        self.cursor.execute(self.SQL_INSERT, (name, address, time, balance))
        self.connection.commit()

    def get_funds(self, name):
        """Return the funds with time for a particular logical account."""
        self.cursor.execute(self.SQL_SELECT, (name, ))
        return self.cursor.fetchall()

