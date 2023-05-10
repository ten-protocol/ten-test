import sqlite3, os


class ContractPersistence:
    """Abstracts the persistence of contract addresses into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS contracts (name TEXT, environment TEXT, address INTEGER, abi STRING)"
    SQL_INSERT = "INSERT INTO contracts VALUES (?, ?, ?, ?)"
    SQL_DELETE = "DELETE from contracts WHERE environment=?"
    SQL_LATEST = "SELECT address, abi FROM contracts WHERE name=? AND environment=? ORDER BY name DESC LIMIT 1"

    def __init__(self, db_dir):
        """Instantiate an instance. """
        self.db = os.path.join(db_dir, 'contracts.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence. """
        self.cursor.execute(self.SQL_CREATE)

    def insert(self, name, environment, address, abi):
        """Insert a new nonce into the persistence. """
        self.cursor.execute(self.SQL_INSERT, (name, environment, address, abi))
        self.connection.commit()

