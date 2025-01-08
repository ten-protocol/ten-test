import sqlite3, os


class ContractPersistence:
    """Abstracts the persistence of contract addresses into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS contracts " \
                 "(name TEXT, environment TEXT, address INTEGER, abi STRING, " \
                 "PRIMARY KEY (name, environment))"
    SQL_INSERT = "INSERT OR REPLACE INTO contracts VALUES (?, ?, ?, ?)"
    SQL_DELETE = "DELETE from contracts WHERE environment=?"
    SQL_SELECT = "SELECT address, abi FROM contracts WHERE name=? AND environment=? ORDER BY name DESC LIMIT 1"

    SQL_CRT_PARAMS = "CREATE TABLE IF NOT EXISTS params " \
                     "(address INTEGER, environment TEXT, key STRING, value STRING, " \
                     "PRIMARY KEY (address, environment, key))"
    SQL_INS_PARAMS = "INSERT OR REPLACE INTO params VALUES (?, ?, ?, ?)"
    SQL_DEL_PARAMS = "DELETE from params WHERE environment=?"
    SQL_SEL_PARAMS = "SELECT value FROM params WHERE address=? AND environment=? AND key=? " \
                     "ORDER BY address DESC LIMIT 1"

    def __init__(self, db_dir):
        """Instantiate an instance."""
        self.db = os.path.join(db_dir, 'contracts.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)
        self.cursor.execute(self.SQL_CRT_PARAMS)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.connection.close()

    def delete_environment(self, environment):
        """Delete all stored contract details for a particular environment."""
        self.cursor.execute(self.SQL_DELETE, (environment, ))
        self.cursor.execute(self.SQL_DEL_PARAMS, (environment, ))
        self.connection.commit()

    def insert_contract(self, name, environment, address, abi):
        """Insert a new contract into the persistence. """
        self.cursor.execute(self.SQL_INSERT, (name, environment, address, abi))
        self.connection.commit()

    def get_contract(self, name, environment):
        """Return the address and abi for a particular deployed contract. """
        self.cursor.execute(self.SQL_SELECT, (name, environment))
        cursor = self.cursor.fetchall()
        if len(cursor) > 0: return cursor[0][0], cursor[0][1]
        return None, None

    def insert_param(self, address, environment, key, value):
        """Insert a parameter for a named contract. """
        self.cursor.execute(self.SQL_INS_PARAMS, (address, environment, key, value))
        self.connection.commit()

    def get_param(self, address, environment, key):
        """Return the address and abi for a particular deployed contract. """
        self.cursor.execute(self.SQL_SEL_PARAMS, (address, environment, key))
        cursor = self.cursor.fetchall()
        if len(cursor) > 0: return cursor[0][0]
        return None