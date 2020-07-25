import mysql, mysql.connector as connector
import pandas as pd
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.pipeline import Pipeline
import numpy as np
import math

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

def filter_by_date(day = None, month = None, year = None):
    """
    Filters data by the specified date and returns data that meets the criterion.

    Parameters
    ----------
    day : (str)
        The day to filter for
    month : (str)
        The month to filter for
    year: (str)
        The year to filter for

    Returns
    ----------
    Data that meets the specified date.
    """
    filters = ["day", "month", "year"]
    params = {"day" : day, "month" : month, "year" : year}
    non_null_params = [(param, params.get(param)) for param in filters if params.get(param) != None] # filter out none types
    q = "SELECT * FROM readings1 WHERE "
    for param in non_null_params:
        q+= f"{param}" # change this to fit WHERE x = y, z = a, etc...
    return q





# For ML Models, we will need to compile a dataset, clean, and structure it: 

data = connect_to_sql(connection = conn, query = q)
raw_df = pd.DataFrame(
    data
)

removeColumns = raw_df.drop(axis=1, columns=["event_name", 'i'])
removeColumns.date = removeColumns.date.apply(lambda d : d.split()[-1].split(':')[0] + " " + d.split()[-1].split(':')[1][-2:]) # get hours and timestamp
def timeConverter(time):
    if time[-2:] == "PM":
        return int(time[:-2]) + 12
    return int(time[:-2])

times = []
[times.append(timeConverter(time)) for time in removeColumns.date]

# one-hot encode
removeColumns.date = times
ohe = pd.get_dummies(removeColumns.date)

# scale the data
scaler = MinMaxScaler()
normalized_sensor_data = pd.DataFrame(scaler.fit_transform(removeColumns.drop(axis =0, columns = ["date"])),
    columns = [
        "dig_button",
        "photoresistor",
        "temp",
        "humidity"
    ]
)
clean_df = pd.concat(
    [normalized_sensor_data, ohe],
    axis=1
)

X, y = clean_df.drop(axis = 0, columns="dig_button"), clean_df.dig_button
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .3, random_state = 42)

default = {"kernel" : "linear", "gamma" : "auto"}
def SVC(df, params = default):
    """
    Build a SVC model with the specified parameters.

    Parameters
    ----------
    df : (str)
        the dataframe to be used for fitting and predicting on the model.
    params : (dict)
        a dictionary of key-value pairs where each key is a valid SVC 
        parameter and each value is the value for that parameter.
    
    Returns
    ----------
    The accuracy of the model
    """
    accepted_params = ["kernel", "gamma"]
    passed_params = [params.get(param) for param in accepted_params]
    if len(passed_params) == len(accepted_params):
        clf = svm.SVC(kernel = params.get("kernel"), gamma = params.get("gamma")).fit(X_train, y_train)
        return clf.score(X_test, y_test)
    clf = svm.SVC().fit(X_train, y_train)
    return clf.score(X_test, y_test)

