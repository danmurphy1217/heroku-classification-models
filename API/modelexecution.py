import mysql, mysql.connector as connector
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import numpy as np

conn = connector.connect(
    user = 'root',
    password = "Dpm#1217",
    host='127.0.0.1',
    database='playground'
)

# sample query
q = (
    "SELECT * FROM readings1;"
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

data = connect_to_sql(connection = conn, query = q)
raw_df = pd.DataFrame(
    data
)

def logreg(pen, sol):
    """
    Build a logistic regression model with the parameters passed

    Parameters
    ----------
    pen : (str)
        the norm that should be used in the penalization. 
        L1 is the manhattan distance and L2 is euclidean.
    sol : (str)
        the solver that should be used for optimization.
        Accepted solvers are lbfgs, liblinear and saga.
    
    Returns
    ----------
    The accuracy of the model along with the model parameters
    """
    X, y = raw_df
    


removeColumns = raw_df.drop(axis=1, columns=["event_name", 'i'])
removeColumns.date = removeColumns.date.apply(lambda d : d.split()[-1].split(':')[0] + " " + d.split()[-1].split(':')[1][-2:]) # get hours and timestamp

removeColumns.date = map(time_converter() , removeColumns.date)
print(removeColumns.date)
ohe_hours = pd.get_dummies(removeColumns.date)
ohe_df = removeColumns.join(
    pd.DataFrame(
        ohe_hours
    )
)
print(ohe_df)