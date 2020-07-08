import mysql.connector as connect
import mysql
import pandas as pd
import numpy as np

# establish connection
connection = connect.connect(
    user = 'root',
    password = "Dpm#1217",
    host='127.0.0.1',
    database='playground'
)

# sample query
query = (
    "SELECT * FROM readings1"
)

def connect_to_sql(connection, query):
    """
    Executes a query statement on a SQL server table. If the query is successful,
    returns the data. If the query is not successful, the error is returned
    @params: connection, a connection instance, and query, a query to execute
    @returns: the data if the query is correct and the error if it is not.
    """
    try:
        # set cursor instance
        cursor = connection.cursor(buffered=True)
        # execute the query
        cursor.execute(query)
        # retrieve data from query
        data_from_query = pd.read_sql_query(
            query,
            connection
        )
        return data_from_query 
    except mysql.connector.Error as e:
        return e

data = connect_to_sql(connection = connection, query = query)
raw_df = pd.DataFrame(
    data
)

def clean_data(data, columns_to_drop):
    """
    returns the cleaned dataset with the specifier columns dropped
    @params: data, a dataset and columns_to_drop, a list of columns to drop from the dataset
    @returns: the cleaned dataset
    """
    data = data.drop(columns_to_drop, axis = 1)
    return data
clean_df = clean_data(raw_df, ['i', 'event_name'])


if __name__ == '__main__':
    print(clean_df)
    connection.close()