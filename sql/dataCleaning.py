import numpy as np
import pandas as pd
import itertools
import datetime
from airtable import Airtable
from dateutil.relativedelta import relativedelta
import calendar

# GLOBAL VARIABLES
global users_df_final_clean, users_df_final
global meetups_df_final_clean, meetups_df_final
global feedback_df_final_clean, feedback_df_final
global months_list
with open("creds.txt", "r") as file:
    credentials = file.read().split('"')
    AIRTABLE_KEY = credentials[1]
    BASE_KEY = credentials[3]

table_names = ["Jammers", "MeetUps", "Feedback"]
months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def retrieve_airtable_data(base, table_name, key):
    """
    A function that pulls in the user data for the specified table.
    @params : base, the base key for a table, table_name, the table_name for a table, and key, the api key.
    @returns : dataframe of each user in the specified table
    """
    airtable = Airtable(base, table_name, api_key=key)
    records_list = airtable.get_all()
    df = pd.DataFrame([record['fields'] for record in records_list])
    return df

def retrieve_airtable_id(base, table_name, key):
    """
    A function that pulls in the ID data for each record in the dataset. The ID is used to track previous connections.
    @params : base, the base key for a table, table_name, the table_name for a table, and key, the api key.
    @returns : dataframe of unique IDs for each user
    """
    airtable = Airtable(base, table_name, api_key=key)
    records_list = airtable.get_all()
    df = pd.DataFrame([record['id'] for record in records_list], columns=["ID"])
    return df

users_df, meetups_df, feedback_df = [retrieve_airtable_data(BASE_KEY, table_names[i], AIRTABLE_KEY) for i in range(len(table_names))]
users_id, meetups_id, feedback_id = [retrieve_airtable_id(BASE_KEY, table_names[i], AIRTABLE_KEY) for i in range(len(table_names))]

def merge_data(id_df, core_df):
    """
    A function that merges the ID and df dataframes together
    @params: id_df, a df filled with ID numbers unique to each user and core_df, a df filled with user data
    @returns: the two dataframes merged together
    """
    return id_df.merge(core_df, left_index=True, right_index=True)

users_df_final, meetups_df_final, feedback_df_final = merge_data(users_id, users_df), merge_data(meetups_id, meetups_df), merge_data(feedback_id, feedback_df)

def clean_data(dataset, airtable_identifier):
    """
    Function that reads in a pandas dataframe and remove spaces in columns, replacing them with underscores.
    This functiuon also renames necessary columns.
    @params: dataset, a pandas dataframe and airtable_identifier, an identifier that tells the function which columns to rename (Users, Meetups or Feedback)
    @returns: cleaned dataset
    """
    dataset.columns = dataset.columns.str.replace(" ", "_")
    if airtable_identifier == "Meetups":
        dataset = dataset.rename(columns = 
                                {
                                    "GB_Group_(from_Active_Users)": "Groups",
                                    "Seniority_(from_Active_Users)": "Seniority"
                                })
    elif airtable_identifier == "Feedback":
        dataset = dataset.rename(columns = 
                                {
                                    "Do_you_think_your_MeetUp_has_helped_you_better_know_the_other_people_that_work_in_GB?" : "better_connected?",
                                    "Round_(from_MeetUps)" : "Round",
                                    "What_was_valuable_about_it?" : "Jam_feedback",
                                    "Anonymous_Feedback_for_UBS" : "Anonymous_feedback",
                                    "General_Feedback" : "General_feedback"
                                })
    elif airtable_identifier == "Users":
        dataset = dataset.drop(axis = 0, index = 0) # drop Shea
        indices_to_drop_Submitted = dataset[dataset.Submitted.isnull()].index
        indices_to_drop_Status = dataset[dataset.Status != "Active"].index
        dataset = dataset.drop(set(indices_to_drop_Submitted.append(indices_to_drop_Status)))
        dataset.index = np.arange(0, len(dataset))
        
    else:
        raise Exception("{} is not an Airtable Identifier. Try 'Users,' 'Meetups,' or 'Feedback'.".format(airtable_identifier))
    
    return dataset

users_df_final_clean, meetups_df_final_clean, feedback_df_final_clean = clean_data(users_df_final, "Users"), clean_data(meetups_df_final, "Meetups"), clean_data(feedback_df_final, "Feedback")
