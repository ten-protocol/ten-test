"""Package of persistence for transaction counts.
"""
import os, sqlite3, mysql.connector
from collections import namedtuple
from ten.test.utils.properties import Properties

DBConnection = namedtuple('DBConnection', 'connection type')


def normalise(statement, _type):
    return statement if _type != 'mysql' else statement.replace('?', '%s')


def get_connection(is_local_ten, is_cloud_vm, user_dir, db):
    '''Get a connection to a db, mysql if running in the cloud and not local testnet, sqlite otherwise.'''
    if not is_local_ten and is_cloud_vm:
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
        connection = sqlite3.connect(os.path.join(user_dir, db))
        return DBConnection(connection, 'sqlite3')


def get_local_connection(user_dir, db):
    '''Get a connection to a db, always local.'''
    connection = sqlite3.connect(os.path.join(user_dir, db))
    return DBConnection(connection, 'sqlite3')