import mysql.connector as connector
from mysql.connector import errorcode
import numpy as np
from airtable import Airtable
import pandas as pd
import sys
from createDatabase import create_database, use_database
from dataCleaning import users_df_final_clean, feedback_df_final_clean, meetups_df_final_clean

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
    "`Skills` TEXT,"
    "`Passion Interests` TEXT,"
    "`Day Preference` VARCHAR(100),"
    "`Time Preference` VARCHAR(100),"
    "`Meetup Preference` TEXT,"
    "`Wanted Skills?` VARCHAR(150),"
    "`Connected Emails` TEXT,"
    "`Wish Connections` VARCHAR(50),"
    "`Submitted` TEXT,"
    "`MeetUps` TEXT,"
    "`Status` VARCHAR(100),"
    "`Previous Connections` TEXT,"
    "`Feedback Provided` VARCHAR(100),"
    "`Preferred Group Size` VARCHAR(100)"
    ")"
) 
TABLES['Feedback'] = (
    "CREATE TABLE `Feedback`("
    "`ID` VARCHAR(25),"
    "`email` VARCHAR(30),"
    "`Good use of Time?` VARCHAR(6),"
    "`What was Most Valuable?` TEXT,"
    "`Better Know Coworkers?` VARCHAR(6),"
    "`NPS` TINYINT,"
    "`General Feedback` TEXT,"
    "`Submitted At` VARCHAR(10),"
    "`User` VARCHAR(30),"
    "`MeetUp` VARCHAR(30),"
    "`Round (From Last Meetup)` VARCHAR(30)"
    ")"
)
TABLES['MeetUps'] = (
    "CREATE TABLE `MeetUps`("
    "`Meetup Number` VARCHAR(25),"
    "`Jammers` TEXT,"
    "`Month` VARCHAR(30),"
    "`Seniority (From Active Users)` TEXT,"
    "`Office (From Active Users)` TEXT,"
    "`GB Group (From Active Users)` TEXT,"
    "`Emails` TEXT,"
    "`Field 8` TEXT,"
    "`Field 9` TEXT,"
    "`Field 10` TEXT"
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

# SQL Query Statements
jammers_insertion_query = """INSERT INTO Jammers (name, email, `GB Group`, Office, Seniority, `Joined UBS`, Skills, `Passion Interests`,
                             `Day Preference`, `Time Preference`, `Meetup Preference`, `Wanted Skills?`, `Connected Emails`, `Wish Connections`, 
                             Submitted, MeetUps, Status, `Previous Connections`, `Feedback Provided`, `Preferred Group Size`)
                             VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

meetups_insertion_query = """INSERT INTO MeetUps (`Meetup Number`, `Jammers`, `Month`, `Seniority (From Active Users)`, `Office (From Active Users)`, 
                                                  `GB Group (From Active Users)`, `Emails`, `Field 8`, `Field 9`, `Field 10`)
                                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""


feedback_insertion_query = """INSERT INTO Feedback (`ID`, `email`, `Good use of Time?`, `What was Most Valuable?`,`Better Know Coworkers?`,`NPS`, 
                                                    `General Feedback`, `Submitted At`, `User`, `MeetUp`, `Round (From Last Meetup)`)
                                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

def data_to_sql(cursor, cnx, data, query):
    """
    prepare data for SQL insertion
    @params: cursor, a mysql.connector().cursor() instance for executing SQL queries, 
             data, a list of tuples, and query,
             the query to execute
    @returns: the state of the SQL query
    """
    records_for_insertion = pd.DataFrame(
        [[", ".join(data.iloc[i][j]) if type(data.iloc[i][j]) == list else data.iloc[i][j] for j in range(len(data.columns))] for i in range(len(data))],
        columns = data.columns
    )
    records_for_insertion_final = ([tuple([records_for_insertion.iloc[i][j] for j in range(len(records_for_insertion.columns))]) for i in range(len(records_for_insertion))])
    try:
        cursor.executemany(
            query,
            records_for_insertion_final
        )
        cnx.commit()
        print(str(cursor.rowcount) + " rows successfully added to the table.")
        
    except connector.Error as err:
        print(f"Exited with error: {err}")
        sys.exit(1)

if __name__ == "__main__":
    # connection to MySQL
    cnx = connector.connect(
        user = "root",
        password = "Dpm#1217",
        host='127.0.0.1'
    )
    cursor = cnx.cursor()

    # data for tables
    users_df_final_clean = users_df_final_clean.drop(
        columns = [
            'ID', 'Which_experience_level_specifically?','MeetUps_copy', 'Admin_Email', 'Which_groups_specifically?'
        ]
    ).fillna("N/A")
    meetups_df_final_clean = meetups_df_final_clean.drop(
        columns = [
            "Feedback_Provided",
            "ID"
        ]
    ).fillna("N/A")
    meetups_df_final_clean.MeetUp_Number = meetups_df_final_clean.MeetUp_Number.astype(str)
    feedback_df_final_clean = feedback_df_final_clean.drop(
        columns = [col for col in feedback_df_final_clean.columns[11:]]
        ).fillna("N/A")
    feedback_df_final_clean.NPS = feedback_df_final_clean.NPS.astype(str)

    # push data to sql
    # create_database( cnx, "Jam" ) # only run once
    use_database( cursor, "Jam" )
    create_tables( cursor, TABLES )
    data_to_sql(cursor, cnx, data = users_df_final_clean, query = jammers_insertion_query)
    data_to_sql(cursor, cnx, data= meetups_df_final_clean, query = meetups_insertion_query) 
    data_to_sql(cursor, cnx, data = feedback_df_final_clean, query = feedback_insertion_query)
    cursor.close()
    cnx.close()

    