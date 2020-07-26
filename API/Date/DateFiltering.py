import pandas as pd
import numpy as np
import mysql, mysql.connector as connector

class Filter:
    def __init__(self, connection):
        self.connection = connection

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
            q+= f"{param[0]} = '{param[1]}' AND " # change this to fit WHERE x = y, z = a, etc...
        q = q[:-5] + ");"
        cursor = connection.cursor(buffered=True)
        cursor.execute(q)
        records = cursor.fetchall()
        return records

if __name__ == "__main__":
    conn = connector.connect(user = 'root', password = "Dpm#1217",\
                            host='127.0.0.1',database='playground')
    data = Filter(connection =conn)
    print(data.Date(connection = conn, day = 21))
