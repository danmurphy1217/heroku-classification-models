import pandas as pd
import numpy as np
import mysql, mysql.connector as connector
import json
class Filter:
    def __init__(self):
        pass
    def Date(self, connection, day = None, month = None, year = None):
        """
        Filters data by the specified date (day, month, and year) and returns data that meets the criterion.

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
        if len(non_null_params) == 0:
            q = "SELECT `day`, `month`, `year`, `photoresistor`, `temp`, `humidity` FROM readings"
            cursor = connection.cursor(buffered=True)
            cursor.execute(q)
            records = cursor.fetchall()
            return records
        q = "SELECT `day`, `month`, `year`, `photoresistor`, `temp`, `humidity` FROM readings WHERE ("
        for param in non_null_params:        
            q+= f"{param[0]} = '{param[1]}' AND "
        q = q[:-5] + ");"
        cursor = connection.cursor(buffered=True)
        cursor.execute(q)
        records = cursor.fetchall()

        df = pd.read_sql_query(q, connection)
        def dict_factory(data):
            """
            A helper function used to convert the data from a mySQL
            query into a dictionary that is JSON serializable.

            Parameters
            ----------
            data : (pandas dataframe)
                df from response of a mySQL query
            
            Returns
            ----------
            the mySQL response converted into a JSON serializable
            dictionary
            """
            cols = data.columns # number of cols

            res = [data.iloc[i].to_dict() for i in range(len(data))] 
            for i in range(len(data)):
                for col in cols:
                    res[i][col] = str(res[i].get(col))
            return res

            
        return dict_factory(df)

