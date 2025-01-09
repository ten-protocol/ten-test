from ten.test.persistence import normalise
from ten.test.persistence import get_connection


class ResultsPersistence:
    """Abstracts the persistence of performance results into a local database.

    Results are a property of the environment and the host that the test was run in. They are externalised so they can
    be visualised outside the test infrastructure.
    """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS results_performance " \
                 "(host VARCHAR(64), " \
                 "test VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "time INTEGER, " \
                 "result REAL, " \
                 "PRIMARY KEY (host, test, environment, time))"
    SQL_INSERT = "INSERT INTO results_performance VALUES (?, ?, ?, ?, ?)"
    SQL_DELETE = "DELETE from results_performance WHERE host=? and environment=?"
    SQL_SELECT = "SELECT time, result FROM results_performance WHERE host=? AND test=? AND environment=? ORDER BY time ASC"

    @classmethod
    def init(cls, is_local_ten, user_dir, host=None, is_cloud=None):
        instance = ResultsPersistence(is_local_ten, user_dir, host, is_cloud)
        instance.create()
        return instance

    def __init__(self, is_local_ten, user_dir, host=None, is_cloud=None):
        """Instantiate an instance."""
        self.host = host
        self.dbconnection = get_connection(is_local_ten, is_cloud, user_dir, 'ten-test.db')
        self.sqlins = normalise(self.SQL_INSERT, self.dbconnection.type)
        self.sqldel = normalise(self.SQL_DELETE, self.dbconnection.type)
        self.sqldel = normalise(self.SQL_SELECT, self.dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()
        self.dbconnection.connection.close()

    def delete_environment(self, environment):
        """Delete all stored performance results for a particular environment."""
        self.cursor.execute(self.sqldel, (self.host, environment))
        self.dbconnection.connection.commit()

    def insert_result(self, test, environment, time, result):
        """Insert a new performance result into the persistence. """
        self.cursor.execute(self.sqlins, (self.host, test, environment, time, result))
        self.dbconnection.connection.commit()

    def get_results(self, test, environment):
        """Return the performance results for a particular test and environment. """
        self.cursor.execute(self.sqlsel, (self.host, test, environment))
        return self.cursor.fetchall()

