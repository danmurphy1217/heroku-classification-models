from Sensors.Photoresistor import Photoresistor
from Sensors.Humidity import Humidity
from Sensors.Temperature import Temperature
import mysql, mysql.connector as connector

def summary(connection, sensor, col):
    """
    Return the summary statistics for the photoresistor data.
    
    Utilizes the Photoresistor class to fetch the data, and build the summary statistics
    for the Photoresistor.

    Parameters
    ----------
    connection : (mysql.connector instance)
        a connection to a mySQL database instance.
    sensor : (class instance)
        instance for the sensor whose data is to be aggregated and returned as summary statistics.
        Acceptable classes are Photoresistor, Humidity, and / or Temperature.
    col : (str)
        A valid column name from the database. This must be either:
        1. photoresistor
        2. humidity
        3. temp

    Returns
    ----------
    the summary statistics (min, max, median, q1, q3 iqr, and number of outliers) for photoresistor data.
    """
    return sensor.summary(sensor.fetchData(connection = connection, query = f"SELECT {col} from readings;")[col])
    
