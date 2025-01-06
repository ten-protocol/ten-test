"""Package of persistence for transaction counts.
"""
import os, sqlite3, mysql.connector
from ten.test.utils.properties import Properties


def get_connection(is_local, db_dir):
    if is_local:
        db = os.path.join(db_dir, 'ten-test.db')
        connection = sqlite3.connect(db)
    else:
        props = Properties()
        config = {
            'host': props.persistence_host(),
            'user': props.persistence_user(),
            'password': props.persistence_password(),
            'database': props.persistence_database()
        }
        connection = mysql.connector.connect(**config)
    return connection