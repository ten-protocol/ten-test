"""Package of persistence for transaction counts.
"""
import os, sqlite3, mysql.connector
from collections import namedtuple
from ten.test.utils.properties import Properties

DBConnection = namedtuple('DBConnection', 'connection type')


def normalise(statement, _type):
    return statement if _type != 'mysql' else statement.replace('?', '%s')


def get_connection(is_cloud_vm, db_dir):
    if is_cloud_vm: pass
    props = Properties()
    config = {
        'host': props.persistence_host(),
        'user': props.persistence_user(),
        'password': props.persistence_password(),
        'database': props.persistence_database(),
        'connection_timeout': 10
    }
    connection1 = mysql.connector.connect(**config)

    db = os.path.join(db_dir, 'ten-test.db')
    connection2 = sqlite3.connect(db)

    return DBConnection(connection1, 'mysql'), DBConnection(connection2, 'sqlite3')