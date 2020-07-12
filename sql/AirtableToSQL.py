import mysql.connector as connector
from mysql.connector import errorcode
import numpy as np
from airtable import Airtable
import pandas as pd
import sys
from createDatabase import create_database, use_database

table_names = ["Jammers", "MeetUps", "Feedback"]

# credentials
with open("creds.txt", "r") as file:
    credentials = file.read().split('"')
    AIRTABLE_KEY = credentials[1]
    BASE_KEY = credentials[3]


def retrieve_airtable_data(base, table_name, key):
    """
    A function that pulls in the user data for the specified table.
    @params : base, the base key for a table, table_name, the table_name for a table, and key, the api key.
    @returns : dataframe of each user in the specified table
    """
    airtable = Airtable(base, table_name, api_key=key)
    records_list = airtable.get_all()
    columns = list([records_list[i]['fields'] for i in range(len(records_list))][0].keys())
    return columns, [tuple(records_list[i]['fields'].values()) for i in range(len(records_list))] # list of tuples, easy to send to SQL

def retrieve_airtable_id(base, table_name, key):
    """
    A function that pulls in the ID data for each record in the dataset. The ID is used to track previous connections.
    @params : base, the base key for a table, table_name, the table_name for a table, and key, the api key.
    @returns : dataframe of unique IDs for each user
    """
    airtable = Airtable(base, table_name, api_key=key)
    records_list = airtable.get_all()
    return [record['id'] for record in records_list]


TABLES = {} # dictionary of the tables to create in SQL
TABLES['Jammers'] = (
    "CREATE TABLE `Jammers`("
    "`name` VARCHAR(30),"
    "`email` VARCHAR(30),"
    "`GB Group` VARCHAR(30),"
    "`Office` VARCHAR(20),"
    "`Seniority` VARCHAR(20),"
    "`Joined UBS` DATE,"
    "`Skills` VARCHAR(100),"
    "`Passion Interests` VARCHAR(100),"
    "`Day Preference` VARCHAR(50),"
    "`Time Preference` VARCHAR(50),"
    "`Meetup Preference` VARCHAR(100),"
    "`Wanted Skills?` VARCHAR(150),"
    "`Connected Emails` TEXT,"
    "`Wish Connections` VARCHAR(50),"
    "`Submitted` DATETIME,"
    "`MeetUps` TEXT,"
    "`Status` VARCHAR(10),"
    "`Previous Connections` TEXT"
    ")"
) 
TABLES['Feedback'] = (
    "CREATE TABLE `Feedback`("
    "`email` VARCHAR(30),"
    "`Good use of Time?` VARCHAR(6),"
    "`What was Most Valuable?` TEXT,"
    "`Better Know Coworkers?` VARCHAR(6),"
    "`NPS` TINYINT,"
    "`General Feedback` TEXT,"
    "`Submitted At` DATE,"
    "`User` VARCHAR(30),"
    "`MeetUp` VARCHAR(30),"
    "`Round (From Last Meetup)` VARCHAR(30)"
    ")"
)
TABLES['MeetUps'] = (
    "CREATE TABLE `MeetUps`("
    "`Meetup Number` SMALLINT,"
    "`Jammers` TEXT,"
    "`Month` VARCHAR(30),"
    "`Seniority (From Active Users)` TEXT,"
    "`Office (From Active Users)` TEXT,"
    "`GB Group (From Active Users)` TEXT,"
    "`Emails` TEXT,"
    "`Field 8` TEXT,"
    "`Field 9` TEXT,"
    "`Field 10` VARCHAR(30)"
    ")"
)

def create_tables(cursor,  tables) -> None:
    """
    returns nothing. Prints out the state of the queries to the console.
    @params: cursor, a mysql.connector().cursor() instance used to execute
             queries and tables, a dictionary where the keys are the names
             of the tables to create and the values are the queries
    @returns: None
    """
    for table in tables:
        table_description = tables[table]
        try:
            print(f"Creating Table {table}.")
            cursor.execute(table_description)
        except connector.Error as error:
            if error.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"{table} already exists.")
            else:
                print(error.msg)
        else:
            print("COMPLETE.")

jammers_insertion_query = """INSERT INTO Jammers (`name`, `email`, `GB Group`, `Office`, `Seniority`, `Joined UBS`, 
                                                  `Skills`, `Passion Interests`, `Day Preference`, `Time Preference`, 
                                                  `Meetup Preference`, `Wanted Skills?`, `Connected Emails`, `Wish Connections`,
                                                  `Submitted`, `MeetUps`, `Status`, `Previous Connections`)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

meetups_insertion_query = """INSERT INTO MeetUps (`Meetup Number`, `Jammers`, `Month`, `Seniority (From Active Users)`, `Office (From Active Users)`, 
                                                  `GB Group (From Active Users)`, `Emails`, `Field 8`, `Field 9`, `Field 10`)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""


feedback_insertion_query = """INSERT INTO Feedback (`email`, `Good use of Time?`, `What was Most Valuable?`,`Better Know Coworkers?`,`NPS`, 
                                                    `General Feedback`, `Submitted At`, `User`, `MeetUp`, `Round (From Last Meetup)`)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

def data_to_sql(cursor, data, TABLE, query):
    """
    prepare data for SQL insertion
    @params: cursor, a mysql.connector().cursor() instance for executing SQL queries, 
             data, a list of tuples, TABLE, the table name to insert into, and query,
             the query to execute
    @returns: the state of the SQL query
    """
    # records_for_insertion = ([tuple([df.iloc[i][j] for j in range(len(df.columns))]) for i in range(len(df))])
    try:
        cursor.executemany(
            query,
            data
        )
        cnx.commit()
        print(str(cursor.rowcount) + " rows successfully added to the table.")
        
    except connector.Error as err:
        print(f"Exited with error: {err}")
        sys.exit(1)

if __name__ == "__main__":
    # Airtable Data
    jammers_columns, jammers_data = retrieve_airtable_data(BASE_KEY, table_names[0], AIRTABLE_KEY)
    jammer_ids = retrieve_airtable_id(BASE_KEY, table_names[0], AIRTABLE_KEY)
    meetups_columns, meetups_data = retrieve_airtable_data(BASE_KEY, table_names[1], AIRTABLE_KEY) 
    feedback_columns, feedback_data = retrieve_airtable_data(BASE_KEY, table_names[2], AIRTABLE_KEY) 

    # connection to MySQL
    connection = connector.connect(
        user = "root",
        password = "Dpm#1217",
        host='127.0.0.1'
    )
    cnx = connection.cursor()
    # create database and tables
    
    # create_database( cnx, "Jam" ) # only run once
    use_database( cnx, "Jam" )
    create_tables( cnx, TABLES )
    # data_to_sql(cursor = cnx, data = jammers_data, TABLE = "Jammers", query = jammers_insertion_query)
    # data_to_sql(cursor = cnx, data= meetups_data, TABLE = "MeetUps", query = meetups_insertion_query) 
    # data_to_sql(cursor = cnx, data = feedback_data, TABLE = "Feedback", query = feedback_insertion_query)
    # [str(data) for i in range(len(jammers_data)) for data in jammers_data[i]]
    