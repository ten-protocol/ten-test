"""Package of persistence for transaction counts.
"""
import os, sqlite3, mysql.connector
from collections import namedtuple
from ten.test.utils.properties import Properties

DBConnection = namedtuple('DBConnection', 'connection type')


def normalise(statement, _type):
    return statement if _type != 'mysql' else statement.replace('?', '%s')


def get_connection(use_remote, user_dir, db):
    '''Get a connection to a db, mysql if use remote, sqlite otherwise.

    If use_remote is false, then the connection will always be to a local database using sqlite3, direction and
    db name specified in the arguments as a backup. If for any reason the remote is requested but is not available,
    then a local database is again used. In general use_remote will be when running non-local testnets in azure, but
    this can be changed for other reasons if needed.
    '''
    if use_remote:
        props = Properties()
        config = {
            'host': props.persistence_host(),
            'user': props.persistence_user(),
            'password': props.persistence_password(),
            'database': props.persistence_database(),
            'connection_timeout': 10
        }
        try:
            connection = mysql.connector.connect(**config)
        except:
            connection = sqlite3.connect(os.path.join(user_dir, db))
            return DBConnection(connection, 'sqlite3')
        return DBConnection(connection, 'mysql')
    else:
        connection = sqlite3.connect(os.path.join(user_dir, db))
        return DBConnection(connection, 'sqlite3')


class LoadablePersistence:

    def __init__(self, use_remote, user_dir, host):
        """Construct an instance. """
        self.host = host
        self.dbconnection = None
        self.cursor = None
        self.sqlins = None
        self.sqlall = None

    def dump(self, file):
        """Dump the contents of the database to csv file. """
        self.cursor.execute(self.sqlall, ())
        with open(file, 'w') as fp:
            for e in self.cursor.fetchall(): fp.write(','.join(map(str, e)) + '\n')

    def load(self, file, batch_size=5000):
        """Load and insert contents into a new database from csv file. """
        def batch_generator(fp):
            batch = []
            for line in fp:
                entries = [x if x != 'None' else None for x in line.strip().split(',')]
                batch.append(entries)
                if len(batch) == batch_size:
                    yield batch
                    batch = []
            if batch: yield batch

        with open(file, 'r') as fp:
            for batch in batch_generator(fp):
                self.cursor.executemany(self.sqlins, batch)

        self.dbconnection.connection.commit()