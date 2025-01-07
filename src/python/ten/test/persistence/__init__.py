"""Package of persistence for transaction counts.
"""
import os, sqlite3, mysql.connector
from collections import namedtuple
from ten.test.utils.properties import Properties

DBConnection = namedtuple('DBConnection', 'connection type')


def normalise(statement, _type):
    return statement if _type != 'mysql' else statement.replace('?', '%s')


def get_connection(is_cloud_vm, db_dir):
    if is_cloud_vm:
        props = Properties()
        config = {
            'host': props.persistence_host(),
            'user': props.persistence_user(),
            'password': props.persistence_password(),
            'database': props.persistence_database(),
            'connection_timeout': 10
        }
        connection = mysql.connector.connect(**config)
        return DBConnection(connection, 'mysql')
    else:
        connection = sqlite3.connect(os.path.join(db_dir, 'ten-test.db'))
        return DBConnection(connection, 'sqlite3')