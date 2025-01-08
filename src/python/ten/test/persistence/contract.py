from ten.test.persistence import normalise
from ten.test.persistence import get_connection


class ContractPersistence:
    """Abstracts the persistence of contract addresses and params into a local database.

    Since a deployed contract is a property of the environment, not the test runner, it should be sharable across
    different test runners when running in the cloud, so the persistence is externalised into a mysql server under these
    conditions.
    """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS contract_details " \
                 "(name VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "address VARCHAR(64), " \
                 "abi MEDIUMTEXT, " \
                 "PRIMARY KEY (name, environment))"
    SQL_INSERT = "INSERT OR REPLACE INTO contract_details VALUES (?, ?, ?, ?)"
    SQL_DELETE = "DELETE from contract_details WHERE environment=?"
    SQL_SELECT = "SELECT address, abi FROM contract_details WHERE name=? AND environment=? ORDER BY name DESC LIMIT 1"

    SQL_CRTPRM = "CREATE TABLE IF NOT EXISTS contract_params " \
                 "(address VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "param_key VARCHAR(64), " \
                 "param_val VARCHAR(64), " \
                 "PRIMARY KEY (address, environment, param_key))"
    SQL_INSPRM = "INSERT OR REPLACE INTO contract_params VALUES (?, ?, ?, ?)"
    SQL_DELPRM = "DELETE from contract_params WHERE environment=?"
    SQL_SELPRM = "SELECT param_val FROM contract_params WHERE address=? AND environment=? AND param_key=? " \
                 "ORDER BY address DESC LIMIT 1"

    @classmethod
    def init(cls, user_dir, host=None, is_cloud=None):
        instance = ContractPersistence(user_dir, host, is_cloud)
        instance.create()
        return instance

    def __init__(self, user_dir, host=None, is_cloud=None):
        """Instantiate an instance (mysql server if on azure, sqlite3 if not)"""
        self.host = host
        self.dbconnection = get_connection(is_cloud, user_dir, 'ten-test.db')
        self.sqlins = normalise(self.SQL_INSERT, self.dbconnection.type)
        self.sqldel = normalise(self.SQL_DELETE, self.dbconnection.type)
        self.sqlsel = normalise(self.SQL_SELECT, self.dbconnection.type)
        self.insprm = normalise(self.SQL_INSPRM, self.dbconnection.type)
        self.delprm = normalise(self.SQL_DELPRM, self.dbconnection.type)
        self.selprm = normalise(self.SQL_SELPRM, self.dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)
        self.cursor.execute(self.SQL_CRTPRM)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()
        self.dbconnection.connection.close()

    def delete_environment(self, environment):
        """Delete all stored contract details for a particular environment."""
        self.cursor.execute(self.sqldel, (environment, ))
        self.cursor.execute(self.delprm, (environment, ))
        self.dbconnection.connection.commit()

    def insert_contract(self, name, environment, address, abi):
        """Insert a new contract into the persistence. """
        self.cursor.execute(self.sqlins, (name, environment, address, abi))
        self.dbconnection.connection.commit()

    def get_contract(self, name, environment):
        """Return the address and abi for a particular deployed contract. """
        self.cursor.execute(self.sqlsel, (name, environment))
        cursor = self.cursor.fetchall()
        if len(cursor) > 0: return cursor[0][0], cursor[0][1]
        return None, None

    def insert_param(self, address, environment, key, value):
        """Insert a parameter for a named contract. """
        self.cursor.execute(self.insprm, (address, environment, key, value))
        self.dbconnection.connection.commit()

    def get_param(self, address, environment, key):
        """Return the address and abi for a particular deployed contract. """
        self.cursor.execute(self.selprm, (address, environment, key))
        cursor = self.cursor.fetchall()
        if len(cursor) > 0: return cursor[0][0]
        return None