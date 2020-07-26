import mysql.connector as connector
from mysql.connector import errorcode
import sys

cnx = connector.connect(
    user = 'root',
    password = "Dpm#1217",
    host='127.0.0.1'
    )
cursor = cnx.cursor()


def create_database(cursor, DB_NAME):
    """
    Creates a MySQL Database
    @params: cursor, a mysql.connector.connect() cursor instance that is used to execute SQL queries and
             DB_NAME, the name of the database to create
    @returns: f"Successfully created {DB_NAME}" if the database is successfully created and the error otherwise
    """
    try:    
        cursor.execute(
            f"CREATE DATABASE {DB_NAME}"
        )
        print(f"Successlly created {DB_NAME}")

    except connector.Error as err:
        print(f"Failed to create {DB_NAME}: {err}")
        sys.exit(1) # use sys.exit rather than exit() since sys module will always be reliable. Non-zero value is an abnormal termination.
                    # 0 is a successful termination.
def use_database(cursor, DB_NAME):
    """
    switches to a database if that database exists. Otherwise it checks to 
    see if the error thrown is ER_BAD_DB_ERROR (meaning the DB does not exist).
    If it is that error, the create_database() helper function is run. Otherwise,
    the error is printed to the console
    @params : cursor, a mysql.connector.cursor() instance for executing queries and
              DB_NAME, the database name
    @returns : the status of the database query
    """
    try:
        cursor.execute(
            f"USE {DB_NAME}" 
        )
        print("Switched to {}".format(DB_NAME))

    except connector.Error as err:
        print(f"Database does not exist: {err}")
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor, DB_NAME)
            cnx.database = DB_NAME
            # call create_database function if the error stated that the database did not exist
        else:
            print(err)
            sys.exit(1) # exit with one and print the error if another error occurs

if __name__ == "__main__":
    use_database(cursor = cursor, DB_NAME = "playground")
    cursor.close()
    cnx.close()
    