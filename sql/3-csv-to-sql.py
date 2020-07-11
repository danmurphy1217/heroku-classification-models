import mysql.connector as connector
import pandas as pd
import sys


cnx = connector.connect(
    user = "root",
    password = "Dpm#1217",
    host='127.0.0.1',
    database='playground'
)
cursor = cnx.cursor()
query = ""

raw_df = pd.read_csv("sql/esp8266readings1.csv")
raw_df = raw_df.drop(
    ["event_name", "Unnamed: 0"],
    axis = 1
)
TABLE = "readings2"

query = """INSERT INTO {} (date, digital_button, photoresistor, temperature, humidity)
               VALUES (%s, %s, %s, %s, %s)""".format(
                TABLE
            )

def data_to_sql(cursor, df, TABLE, query):
    """
    prepare data for SQL insertion
    @params: cursor, a mysql.connector().cursor() instance for executing SQL queries, 
             df, a pandas dataframe, and TABLE, the table name to insert into
    @returns: the state of the SQL query
    """
    records_for_insertion = ([tuple([df.iloc[i][j] for j in range(len(df.columns))]) for i in range(len(df))])

    try:
        cursor.executemany(
            query,
            records_for_insertion
        )
        cnx.commit()
        print(str(cursor.rowcount) + " rows successfully added to the table.")
        
    except connector.Error as err:
        print(f"Exited with error: {err}")
        sys.exit(1)

if __name__ == "__main__":
    raw_df.digital_button, raw_df.photoresistor = raw_df.digital_button.astype(str), raw_df.photoresistor.astype(str)
    data_to_sql(
        cursor, 
        raw_df,
        TABLE,
        query
    )
    cursor.close()
    cnx.close()
