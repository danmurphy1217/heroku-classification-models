from mysql.connector import connect
import numpy as np

connection = connect(
    user = 'root',
    password = 'Dpm#1217',
    host = '127.0.0.1',
    database = 'playground'
)
cursor = connection.cursor()

query = (
    "SELECT * FROM readings1"
)

def query_data(connection, cursor, query):
    """
    Returns data from MySql Server that fits the specified query. 
    @params: query, the query to be used
    @returns: data from MySQL Server
    """
    # store data from Query
    data = np.empty(
        [5381, 6],
        dtype = str
    )

    # execute query
    cursor.execute(query)

    index_list = []
    date_list = []
    dig_button_list = []
    photoresistor_val_list = []
    temp_list = []
    humidity_list = []
    # loop through tuple & unpack
    for index, date, event_name, dig_button, photoresistor_val, temp, humidity in cursor:
        index_list.append(index)
        date_list.append(date)
        dig_button_list.append(dig_button)
        photoresistor_val_list.append(photoresistor_val)
        temp_list.append(temp)
        humidity_list.append(humidity)
    return index_list, date_list, dig_button_list, photoresistor_val_list, temp_list, humidity_list

index_list, date_list, dig_button_list, photoresistor_val_list, temp_list, humidity_list = query_data(connection, cursor, query)
clean_index_list = [int(index) for index in index_list]
clean_date_list = [date.encode('utf-8') for date in date_list]
clean_temp_list = [float(temp) for temp in temp_list]
clean_humidity_list = [float(humidity) for humidity in humidity_list]
            
        
if __name__ == '__main__':
    pass