import mysql, mysql.connector as connector
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


class StructureData:
    def __init__(self, connection, query):
        self.connection = connection
        self.query = query
        
    def fetchData(self, connection, query):
        """Establish a connection to mySQL database and return the data in a pandas dataframe"""
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            cursor.fetchall()
            return pd.read_sql_query(
                query, connection
            )
        except mysql.connector.ConnectionError as e:
            return f"Error: {e}"


    def cleanData(self, data):
        """
        Receives a dataframe as input and cleans and structures the data.

        First, the data is read in through the fetchData method previously defined.
        Then, the sensor data is normalized and the hours of the times are one-hot-
        encoded. Then, the X and y datasets are returned from the function.

        Parameters
        ----------
        data : (pandas dataframe)
            A pandas dataframe containing all of the data in a mySQL table.

        Returns
        ----------
        A cleaned a structured dataframe prepared for machine learning.
        """
        def timeConversion(time):
            """A helper function for `c` that converts AM and PM timestamps into 24-hour times"""
            if time[-2:] == "PM":
                return int(time[:-2]) + 12
            return int(time[:-2])
        
        data.date = data.date.apply(lambda d : d.split()[-1].split(':')[0] + " " + d.split()[-1].split(':')[1][-2:]) # get hours and timestamp
        times = []
        [times.append(timeConversion(time)) for time in data.date]
        data.date = times # 24 hour time

        # one-hot encoding
        ohe = pd.get_dummies(data.date)

        # scale the data: normalization
        scaler = MinMaxScaler()
        normalized_sensor_data = pd.DataFrame(scaler.fit_transform(data.drop(axis =0, columns = ["date", "day", "month", "year"])),
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
        X, y = clean_df.drop(axis = 0, columns="dig_button"), clean_df.dig_button.astype(int)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .3, random_state = 42)

        return X_train, X_test, y_train, y_test


conn = connector.connect(user = 'root', password = "Dpm#1217",\
                            host='127.0.0.1',database='playground')                      
model = StructureData(connection=conn, query = "SELECT * FROM readings;")
sql_data = model.fetchData(conn, query = "SELECT * FROM readings;" )
X_train, X_test, y_train, y_test = model.cleanData(sql_data) # for use in SVC.py
