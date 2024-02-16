import sqlite3, os


class FundsPersistence:
    """Abstracts the persistence of contract addresses into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS funds " \
                 "(name TEXT, address INTEGER, time INTEGER, balance INTEGER, " \
                 "PRIMARY KEY name)"
    SQL_INSERT = "INSERT OR REPLACE INTO funds VALUES (?, ?, ?, ?)"
    SQL_DELETE = "DELETE from funds WHERE name=? and address=?"
    SQL_SELECT = "SELECT time, balance FROM funds WHERE name=? and address=? ORDER BY time DESC"

    def __init__(self, db_dir):
        """Instantiate an instance."""
        self.db = os.path.join(db_dir, 'contracts.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.connection.close()

    def delete_name(self, name):
        """Delete all stored contract details for a particular environment."""
        self.cursor.execute(self.SQL_DELETE, (name, ))
        self.connection.commit()

    def insert_balance(self, name, address, time, balance):
        """Insert a new contract into the persistence. """
        self.cursor.execute(self.SQL_INSERT, (name, address, time, balance))
        self.connection.commit()

    def get_balance(self, name, environment):
        """Return the address and abi for a particular deployed contract. """
        self.cursor.execute(self.SQL_SELECT, (name, environment))
        cursor = self.cursor.fetchall()
        if len(cursor) > 0: return cursor[0][0], cursor[0][1]
        return None, None
