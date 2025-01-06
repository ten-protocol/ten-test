from ten.test.persistence import normalise

class ContractPersistence:
    """Abstracts the persistence of contract addresses into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS contracts " \
                 "(name VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "address INTEGER, " \
                 "abi MEDIUMTEXT, " \
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

    def __init__(self, dbconnection):
        """Instantiate an instance."""
        self.dbconnection = dbconnection
        self.insert = normalise(self.SQL_INSERT, dbconnection.type)
        self.delete = normalise(self.SQL_DELETE, dbconnection.type)
        self.select = normalise(self.SQL_SELECT, dbconnection.type)
        self.crt_params = normalise(self.SQL_CRT_PARAMS, dbconnection.type)
        self.ins_params = normalise(self.SQL_INS_PARAMS, dbconnection.type)
        self.del_params = normalise(self.SQL_DEL_PARAMS, dbconnection.type)
        self.sel_params = normalise(self.SQL_SEL_PARAMS, dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)
        self.cursor.execute(self.SQL_CRT_PARAMS)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()

    def delete_environment(self, environment):
        """Delete all stored contract details for a particular environment."""
        self.cursor.execute(self.delete, (environment, ))
        self.cursor.execute(self.del_params, (environment, ))
        self.dbconnection.connection.commit()

    def insert_contract(self, name, environment, address, abi):
        """Insert a new contract into the persistence. """
        self.cursor.execute(self.insert, (name, environment, address, abi))
        self.dbconnection.connection.commit()

    def get_contract(self, name, environment):
        """Return the address and abi for a particular deployed contract. """
        self.cursor.execute(self.select, (name, environment))
        cursor = self.cursor.fetchall()
        if len(cursor) > 0: return cursor[0][0], cursor[0][1]
        return None, None

    def insert_param(self, address, environment, key, value):
        """Insert a parameter for a named contract. """
        self.cursor.execute(self.ins_params, (address, environment, key, value))
        self.dbconnection.connection.commit()

    def get_param(self, address, environment, key):
        """Return the address and abi for a particular deployed contract. """
        self.cursor.execute(self.sel_params, (address, environment, key))
        cursor = self.cursor.fetchall()
        if len(cursor) > 0: return cursor[0][0]
        return None