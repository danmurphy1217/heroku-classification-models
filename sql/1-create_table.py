import mysql, mysql.connector as connector 
import numpy as np
import pandas as pd
from mysql.connector import errorcode


df = pd.read_csv('esp8266readings1.csv')

# SQL db name
db_name = 'playground'
TABLES = {}
TABLES['readings2'] = (
    "CREATE TABLE `readings2`("
    "`index` VARCHAR(15),"
    "`date` VARCHAR(100),"
    "`digital button` TINYINT(1),"
    "`photoresistor` MEDIUMINT,"
    "`temperature` DECIMAL(4, 2),"
    "`humidity` DECIMAL(4, 2)"
    ")"
) 

cnx = connector.connect(
    user = 'root',
    password = "Dpm#1217",
    host='127.0.0.1',
    database='playground'
)
cursor = cnx.cursor()

for table in TABLES:
    table_description = TABLES[table]
    try:
        print(f"Creating Table {table}.")
        cursor.execute(table_description)
    except mysql.connector.Error as error:
        if error.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print(f"{table} already exists.")
        else:
            print(error.msg)
    else:
        print("COMPLETE.")
    


if __name__ == '__main__':
    cursor.close()
    cnx.close()
    