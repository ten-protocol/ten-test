from ten.test.persistence import normalise


class ResultsPersistence:
    """Abstracts the persistence of performance results into a local database. """

    SQL_CREATE = "CREATE TABLE IF NOT EXISTS results " \
                 "(test VARCHAR(64), " \
                 "environment VARCHAR(64), " \
                 "time INTEGER, " \
                 "result REAL, " \
                 "PRIMARY KEY (test, environment, time))"
    SQL_INSERT = "INSERT INTO results VALUES (?, ?, ?, ?)"
    SQL_DELETE = "DELETE from results WHERE environment=?"
    SQL_SELECT = "SELECT time, result FROM results WHERE test=? AND environment=? ORDER BY time ASC"

    def __init__(self, dbconnection):
        """Instantiate an instance."""
        self.dbconnection = dbconnection
        self.insert = normalise(self.SQL_INSERT, dbconnection.type)
        self.delete = normalise(self.SQL_DELETE, dbconnection.type)
        self.select = normalise(self.SQL_SELECT, dbconnection.type)
        self.cursor = self.dbconnection.connection.cursor()

    def create(self):
        """Create the cursor to the underlying persistence."""
        self.cursor.execute(self.SQL_CREATE)

    def close(self):
        """Close the connection to the underlying persistence."""
        self.cursor.close()

    def delete_environment(self, environment):
        """Delete all stored performance results for a particular environment."""
        self.cursor.execute(self.delete, (environment, ))
        self.dbconnection.connection.commit()

    def insert_result(self, test, environment, time, result):
        """Insert a new performance result into the persistence. """
        self.cursor.execute(self.insert, (test, environment, time, result))
        self.dbconnection.connection.commit()

    def get_results(self, test, environment):
        """Return the performance results for a particular test and environment. """
        self.cursor.execute(self.select, (test, environment))
        return self.cursor.fetchall()

