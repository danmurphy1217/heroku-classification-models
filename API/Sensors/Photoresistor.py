import mysql, mysql.connector as connector
import pandas as pd
import numpy as np

class Photoresistor:
    def __init__(self, connection):
        self.connection = connection
        
    def fetchData(self, connection, query):
        """Establish a connection to mySQL database and return the data in a pandas dataframe"""
        try:
            cursor = connection.cursor()
            return pd.read_sql_query(
                query, connection
            )
        except ConnectionError as e:
            return f"Error: {e}"
    def summary(self, data):
        """
        Returns summary statistics about the data source.

        Calculates the minimum, maximum, q1, q3, iqr, median, and number of outliers
        for the specified data source, which should be a column of data (whether that
        data be fetched from a remote database or a local pandas dataframe).

        Parameters
        ----------
        data : (one-dimensional array / series)
            The column of data used for calculating the summary statistics.
            This column must contain data that is type float or int.

        Returns
        ----------
        The summary statistics for the column of data provided
        """
        try:
            data = data.astype(int)
            minimum, maximum = min(data), max(data)
            q1, q3 = np.percentile(data, 25), np.percentile(data, 75)
            iqr = q3 - q1
            median = np.median(data)
            lowerOutliers = [val for val in data if int(val) < (q1 - 1.5*iqr)]
            upperOutliers = [val for val in data if int(val) > (q3 + 1.5*iqr)]
            return {
                "min" : minimum,
                "max" : maximum,        
                "q1" : q1,
                "q3" : q3,
                "iqr" : iqr,
                "median" : median,
                "num_outliers" : len(lowerOutliers) + len(upperOutliers)
            }
        except ValueError as e:
            return {"error" : e}

