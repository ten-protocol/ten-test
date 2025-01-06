"""Package of persistence for transaction counts.
"""
import os, sqlite3, mysql.connector
from collections import namedtuple
from ten.test.utils.properties import Properties

DBConnection = namedtuple('DBConnection', 'connection type')


def get_connection(is_local, db_dir):
    #if is_local:
    db = os.path.join(db_dir, 'ten-test.db')
    connection1 = sqlite3.connect(db)
    #else:
    props = Properties()
    config = {
            'host': props.persistence_host(),
            'user': props.persistence_user(),
            'password': props.persistence_password(),
            'database': props.persistence_database(),
            'connection_timeout': 10
    }
    connection2 = mysql.connector.connect(**config)
    return DBConnection(connection1, 'sqlite3'), DBConnection(connection2, 'mysql')