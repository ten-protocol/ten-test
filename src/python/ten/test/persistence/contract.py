from ten.test.persistence import normalise


class ContractPersistence:
    """Abstracts the persistence of contract addresses into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS contracts " \
                 "(host VARCHAR(64), " \
                 "name VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "address VARCHAR(64), " \
                 "abi MEDIUMTEXT, " \
                 "PRIMARY KEY (host, name, environment))"
    SQL_INSERT = "INSERT OR REPLACE INTO contracts VALUES (?, ?, ?, ?, ?)"
    SQL_DELETE = "DELETE from contracts WHERE host=? AND environment=?"
    SQL_SELECT = "SELECT address, abi FROM contracts WHERE host=? AND name=? AND environment=? ORDER BY name DESC LIMIT 1"

    SQL_CRTPRM = "CREATE TABLE IF NOT EXISTS params " \
                 "(host VARCHAR(64), " \
                 "address VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "key VARCHAR(64), " \
                 "value VARCHAR(64), " \
                 "PRIMARY KEY (host, address, environment, key))"
    SQL_INSPRM = "INSERT OR REPLACE INTO params VALUES (?, ?, ?, ?, ?)"
    SQL_DELPRM = "DELETE from params WHERE host=? AND environment=?"
    SQL_SELPRM = "SELECT value FROM params WHERE host=? AND address=? AND environment=? AND key=? " \
                 "ORDER BY address DESC LIMIT 1"

    @classmethod
    def init(cls, host, dbconnection):
        instance = ContractPersistence(host, dbconnection)
        instance.create()
        return instance

    def __init__(self, host, dbconnection):
        """Instantiate an instance."""
        self.host = host
        self.dbconnection = dbconnection
        self.insert = normalise(self.SQL_INSERT, dbconnection.type)
        self.delete = normalise(self.SQL_DELETE, dbconnection.type)
        self.select = normalise(self.SQL_SELECT, dbconnection.type)
        self.crtprm = normalise(self.SQL_CRTPRM, dbconnection.type)
        self.insprm = normalise(self.SQL_INSPRM, dbconnection.type)
        self.delprm = normalise(self.SQL_DELPRM, dbconnection.type)
        self.selprm = normalise(self.SQL_SELPRM, dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)
        self.cursor.execute(self.SQL_CRTPRM)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()

    def delete_environment(self, environment):
        """Delete all stored contract details for a particular environment."""
        self.cursor.execute(self.delete, (self.host, environment))
        self.cursor.execute(self.delprm, (self.host, environment))
        self.dbconnection.connection.commit()

    def insert_contract(self, name, environment, address, abi):
        """Insert a new contract into the persistence. """
        self.cursor.execute(self.insert, (self.host, name, environment, address, abi))
        self.dbconnection.connection.commit()

    def get_contract(self, name, environment):
        """Return the address and abi for a particular deployed contract. """
        self.cursor.execute(self.select, (self.host, name, environment))
        cursor = self.cursor.fetchall()
        if len(cursor) > 0: return cursor[0][0], cursor[0][1]
        return None, None

    def insert_param(self, address, environment, key, value):
        """Insert a parameter for a named contract. """
        self.cursor.execute(self.insprm, (self.host, address, environment, key, value))
        self.dbconnection.connection.commit()

    def get_param(self, address, environment, key):
        """Return the address and abi for a particular deployed contract. """
        self.cursor.execute(self.selprm, (self.host, address, environment, key))
        cursor = self.cursor.fetchall()
        if len(cursor) > 0: return cursor[0][0]
        return None