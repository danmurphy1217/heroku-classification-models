# libraries in use
import os.path
from googleapiclient.discovery import build
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import mysql.connector as connector, mysql
from mysql.connector import errorcode
import sys



"""
Part 1: interact with Sheets API and query the data
"""
# for interacting with Google Sheets API
SPREADSHEET_ID = "1F-UPZf3je1x4M8ryp34OCe29E-CagCrUn9mFzsyfmJE"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def main() -> list:
    """
    function that verifies credentials for google sheets API and, if the verification
    is successful, returns the requested data (columns A - E in this scenario).
    @params: None
    @returns: the queried data from sheets.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0) # user log-in
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
    service = build('sheets', 'v4', credentials= creds)

    # Sheets API
    sheets = service.spreadsheets()
    result = sheets.values().get(
        spreadsheetId = SPREADSHEET_ID,
        range = 'A:E' # CHANGE IF NEEDED
    ).execute()
    return result.get("values")

sheets_data = main()
# list of tuples for sending to SQL
preprocess_for_sql = [tuple(data) for data in sheets_data]



"""
Part 2: Interact with MySQL and send the queried Google Sheets data -> MySql
"""
# establish connection to MySQL
cnx = connector.connect(
    user = 'root',
    password = "Dpm#1217",
    host='127.0.0.1',
    database='playground'
)
cursor = cnx.cursor()
TABLE = 'sheetsToSQL' # name of table
# Query to execute -> should be an INSERT statement
QUERY = """INSERT INTO {} (`date`, `event_name`, `digital button`, `photoresistor`, `temperature; humidity`)
               VALUES (%s, %s, %s, %s, %s)""".format(
                TABLE
            )

def create_table(table: str, connector: classmethod, cursor: classmethod) -> None:
    """
    creates a DQL table with the provided table name.
    @params: table, the name of the table, connector, a mysql.connector class instance,
             and cursor, a mysql.connector.cursor() instance used for executing the queries
    """
    TABLES = {}
    # statement for creating the table
    # add for loop here if creating multiple tables
    TABLES[table] = (
        "CREATE TABLE `sheetsToSQL`("
        "`date` VARCHAR(100),"
        "`event_name` VARCHAR(16),"
        "`digital button` TINYINT(1),"
        "`photoresistor` MEDIUMINT,"
        "`temperature; humidity` VARCHAR(14)"
        ")"
    )
    # only loops once since creating one table
    for table in TABLES:
        table_description = TABLES[table]
    try:
        print(f"Creating Table {table}.")
        cursor.execute(table_description) # execute statement
    except mysql.connector.Error as error:
        if error.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print(f"{table} already exists.")
        else:
            print(error.msg)
    else:
        print("COMPLETE.")

def query_sql(query: str, data: list) -> None:
    """
    adds data to an already-existent SQL Table. 
    @params: query, the SQL query to execute (This query should be a SQL INSERT statement)
             and data, the data to insert into the SQL Table.
    @returns: the number of rows added to the table if successful. If not successful,
              returns the error and exits from the Python Interpreter.
    """
    try:
        # executemany used for adding multiple rows to table
        cursor.executemany(
            query,
            data
        )
        cnx.commit() # must use commit() to commit query
        print(str(cursor.rowcount) + " rows successfully added to the table.")
        
    except connector.Error as err:
        print(f"Exited with error: {err}")
        sys.exit(1)

if __name__ == "__main__":
    # create table in SQL
    create_table(TABLE, cnx, cursor)
    # append preprocessed data to SQL Table
    query_sql(query = QUERY, data = preprocess_for_sql[1:])
    # close connection
    cursor.close()
    cnx.close()