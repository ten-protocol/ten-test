import sqlite3, os


class ResultsPersistence:
    """Abstracts the persistence of performance results into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS results " \
                 "(test TEXT, environment TEXT, time INTEGER, result REAL, " \
                 "PRIMARY KEY (test, environment, time))"
    SQL_INSERT = "INSERT INTO results VALUES (?, ?, ?, ?)"
    SQL_DELETE = "DELETE from results WHERE environment=?"
    SQL_SELECT = "SELECT time, result FROM results WHERE test=? AND environment=? ORDER BY time ASC"

    def __init__(self, db_dir):
        """Instantiate an instance."""
        self.db = os.path.join(db_dir, 'results.db')
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.connection.close()

    def delete_environment(self, environment):
        """Delete all stored performance results for a particular environment."""
        self.cursor.execute(self.SQL_DELETE, (environment, ))
        self.connection.commit()

    def insert_result(self, test, environment, time, result):
        """Insert a new performance result into the persistence. """
        self.cursor.execute(self.SQL_INSERT, (test, environment, time, result))
        self.connection.commit()

    def get_results(self, test, environment):
        """Return the performance results for a particular test and environment. """
        self.cursor.execute(self.SQL_SELECT, (test, environment))
        return self.cursor.fetchall()

