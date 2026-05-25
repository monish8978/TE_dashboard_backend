"""
Import configuration settings from the settings module.
"""
from settings import mysql_info, download_csv_row_data, download_csv_live_current_row_data, compute_layer_function_log_path, Threshold

"""
Import necessary modules for functionality and error handling.
"""
from datetime import datetime
from pytz import timezone  # For timezone handling
import pandas as pd  # For data manipulation and analysis
import traceback  # For extracting, formatting, and printing exceptions
import fnmatch  # For file name pattern matching
import pymysql  # For MySQL database interaction
import logging  # For logging events
import threading  # Module to handle multi-threading
import json  # For JSON data handling
import time  # For time-related functions
import os  # For operating system functionalities
import warnings  # For managing warnings

# Suppress warnings to keep log output clean
warnings.filterwarnings("ignore")

# Setting up logging to track the program's execution
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)s - %(message)s',  # Define the format of log messages
    level=logging.INFO,  # Set the logging level to INFO to capture informational messages
    filename=compute_layer_function_log_path  # Specify the log file to write log messages to
)

# Initialize the main logger
log = logging.getLogger('__main__')  # Get a logger specifically for the main module

# Initialize a threading lock for thread synchronization
lock = threading.Lock()  # Create a lock object to ensure thread-safe operations


def sql_conn():

        """
                Handing for sql connection.
                Args:-
                        There is no need to use any args just use the configuration variable from config file.
                Return:
                        db:- Return database object after crete database connection
        """
        db = ""
        cur = ""
        try:
                db = pymysql.connect(host=mysql_info['host'],user=mysql_info['user'],password= mysql_info['password'],db=mysql_info['database'])
                # Create a connection to the MySQL database
        except Exception as err:
                log.error("Not Able to connect mysql reason is "+str(err))
                traceback.print_exc()
        return db

def get_date():
    """
    This function retrieves the current date in 'YYYY-MM-DD' format.
    If an error occurs during the process, it logs the error message and the traceback.
    """
    try:
        # Get the current date and format it as 'YYYY-MM-DD'
        today_date = datetime.now().strftime('%Y-%m-%d')
        return today_date
    except Exception as err:
        # Log the error message if an exception occurs
        log.error(str(err))
        # Print the traceback of the exception for debugging purposes
        traceback.print_exc()

def read_csv_files(
    selected_campaign_name,
    start_date,
    end_date,
    today_date,
    selected_campaign_type,
    selected_agent_filter,
    selected_skills_name,
    selected_list_name
):
    """
    Reads CSV files for SINGLE / MULTIPLE / ALL campaigns and returns combined DataFrame.
    """

    try:
        # =========================
        # DATE CONVERSION
        # =========================
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.min.time())
        today_date = datetime.strptime(today_date, "%Y-%m-%d")

        # =========================
        # GET ALL CAMPAIGNS FUNCTION
        # =========================
        def get_all_campaign_folders():
            return [
                d for d in os.listdir(download_csv_row_data)
                if os.path.isdir(os.path.join(download_csv_row_data, d))
            ]

        # =========================
        # CAMPAIGN HANDLING
        # =========================
        if selected_campaign_name == "ALL":
            campaign_list = get_all_campaign_folders()
            if "campaignname" in campaign_list:
                campaign_list.remove("campaignname")
        else:
            campaign_list = [
                c.strip() for c in str(selected_campaign_name).split(",")
                if c.strip()
            ]

        combined_df = pd.DataFrame()

        # =========================
        # LOOP ALL CAMPAIGNS
        # =========================
        for campaign in campaign_list:
            # Decide folder path
            if start_date == today_date == end_date:
                folder_path = f"{download_csv_live_current_row_data}{campaign}/"
            else:
                if campaign != "campaignname":
                    folder_path = f"{download_csv_row_data}{campaign}/"
                

            all_files = []

            # Collect CSV files
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if fnmatch.fnmatch(file, "*.csv"):
                        all_files.append(os.path.join(root, file))

            # Read files
            for file_path in all_files:
                try:
                    file_date_str = file_path.split("/")[-1].split(".")[0]
                    file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                except:
                    continue

                if start_date <= file_date <= end_date:
                    try:
                        df = pd.read_csv(file_path)
                    except:
                        columns = [
                            'agent_id', 'agent_name', 'campaign_id',
                            'campaign_name', 'wrapup_time', 'call_duration',
                            'wait_time', 'call_status_disposition',
                            'next_call_time', 'campaign_type',
                            'q_enter_time', 'q_leave_time',
                            'call_start_date_time', 'call_end_date_time'
                        ]
                        df = pd.DataFrame(columns=columns)

                    combined_df = pd.concat([combined_df, df], ignore_index=True)

        # =========================
        # FILTER: AGENT
        # =========================
        if selected_agent_filter != "ALL" and not combined_df.empty:
            try:
                combined_df = combined_df[
                    combined_df['agent_id'] == int(selected_agent_filter)
                ]
            except:
                pass

        # =========================
        # FILTER: SKILLS
        # =========================
        if selected_skills_name != "ALL" and not combined_df.empty:
            combined_df = combined_df[
                combined_df['skills'] == selected_skills_name
            ]

        # =========================
        # FILTER: LIST NAME
        # =========================
        if selected_list_name != "ALL" and not combined_df.empty:
            combined_df = combined_df[
                combined_df['list_name'] == selected_list_name
            ]

        # =========================
        # FILTER: CAMPAIGN TYPE
        # =========================
        if selected_campaign_type != "ALL" and not combined_df.empty:
            if selected_campaign_type in ["INBOUND", "OUTBOUND"]:
                combined_df = combined_df[
                    combined_df['campaign_type'] == selected_campaign_type
                ]

        # =========================
        # EMPTY SAFE DATAFRAME
        # =========================
        if combined_df.empty:
            columns = [
                'agent_id', 'agent_name', 'campaign_id', 'campaign_name',
                'wrapup_time', 'call_duration', 'wait_time',
                'call_status_disposition', 'next_call_time',
                'campaign_type', 'q_enter_time', 'q_leave_time',
                'call_start_date_time', 'call_end_date_time'
            ]
            combined_df = pd.DataFrame(columns=columns)

        return combined_df

    except Exception as err:
        log.error(str(err))
        traceback.print_exc()

def get_campaign_id(mydb, selected_campaign_name):
    """
    Retrieves the campaign ID from the database for a given campaign name.

    Args:
    - mydb (pymysql.connections.Connection): The database connection object.
    - selected_campaign_name (str): The name of the campaign for which the ID is to be retrieved.

    Returns:
    - int: The campaign ID if found, otherwise 0.
    """
    try:
        # Execute SQL query to fetch campaign_id and campaign_name from the 'campaign' table
        query = f"SELECT campaign_id, campaign_name FROM campaign WHERE campaign_name = '{selected_campaign_name}'"
        tmp_campaign_id = pd.read_sql(query, con=mydb)

        # Attempt to retrieve the campaign_id value from the resulting DataFrame
        try:
            if not tmp_campaign_id.empty:
                # Access the first row of the DataFrame and get the 'campaign_id' value
                campaign_id_value = tmp_campaign_id.loc[0, 'campaign_id']
            else:
                campaign_id_value = 0
        except IndexError:
            # If the DataFrame is empty or the index is not available, set campaign_id_value to 0
            campaign_id_value = 0

        return campaign_id_value
    except Exception as err:
        # Log any exceptions that occur and print the traceback for debugging
        log.error(str(err))
        traceback.print_exc()
        # Optionally, you may return a default value or re-raise the exception depending on your use case
        return 0


def agent_live_sql(mydb, campaign_id_value):
    """
    Fetches live data for agents from the database based on the given campaign ID.

    Args:
    - mydb (pymysql.connections.Connection): The database connection object.
    - campaign_id_value (int): The campaign ID to filter the data by.

    Returns:
    - pd.DataFrame: A DataFrame containing the live data for agents.
    """
    try:
        # Define the SQL query to retrieve live data from the 'agent_live' table
        query = """
        SELECT
            agent_state,
            dialer_type,
            campaign_type,
            closer_time,
            last_activity_time
        FROM
            agent_live
        WHERE
            campaign_id = %s
        """

        # Execute the SQL query and load the result into a DataFrame
        agent_live_df = pd.read_sql(query, con=mydb, params=(campaign_id_value,))

        # Return the DataFrame containing the live data
        return agent_live_df

    except Exception as err:
        # Log any exceptions that occur and print the traceback for debugging
        log.error(str(err))
        traceback.print_exc()
        # Optionally, return an empty DataFrame or handle the exception as needed
        return pd.DataFrame()


def QueueLiveSql(mydb, selected_campaign_name):
    """
    Fetches live data for agents in the queue from the database based on the given campaign name.

    Args:
    - mydb (pymysql.connections.Connection): The database connection object.
    - selected_campaign_name (str): The name of the campaign to filter the data by.

    Returns:
    - pd.DataFrame: A DataFrame containing the live data for agents in the queue.
    """
    try:
        # Define the SQL query to retrieve queue data from the 'queue_live' table
        query = """
        SELECT
            q_enter_time,
            cust_ph_no
        FROM
            queue_live
        WHERE
            campaign_name = %s
        """

        # Execute the SQL query and load the result into a DataFrame
        agent_in_queue_df = pd.read_sql(query, con=mydb, params=(selected_campaign_name,))

        # Return the DataFrame containing the queue data
        return agent_in_queue_df

    except Exception as err:
        # Log any exceptions that occur and print the traceback for debugging
        log.error(str(err))
        traceback.print_exc()
        # Optionally, return an empty DataFrame or handle the exception as needed
        return pd.DataFrame()


def IvrRepportSql(mydb, selected_campaign_name):
    """
    Fetches live IVR report data from the database for the given campaign name.

    Args:
    - mydb (pymysql.connections.Connection): The database connection object.
    - selected_campaign_name (str): The name of the campaign to filter the data by.

    Returns:
    - pd.DataFrame: A DataFrame containing the IVR report data for the current date and the specified campaign.
    """
    try:
        # Define the SQL query to retrieve IVR report data for the current date and the specified campaign
        query = """
        SELECT
            entrytime,
            CampaignTransfer,
            duration
        FROM
            ivr_report_current_report
        WHERE
            DATE(last_updated) = CURRENT_DATE()
            AND CampaignTransfer = %s
        """

        # Execute the SQL query and load the result into a DataFrame
        IVRSql = pd.read_sql(query, con=mydb, params=(selected_campaign_name,))

        # Return the DataFrame containing the IVR report data
        return IVRSql

    except Exception as err:
        # Print the traceback of the exception for debugging
        traceback.print_exc()
        # Log the error message
        log.error(str(err))
        # Optionally, return an empty DataFrame or handle the exception as needed
        return pd.DataFrame()


def average_handling_time(sql):
    """
    Computes the average handling time for live and historical data from a DataFrame.

    Args:
    - sql (pd.DataFrame): DataFrame containing columns 'wrapup_time' and 'call_duration' to compute the average handling time.

    Returns:
    - dict: A dictionary with the key 'average_handling_time' and its computed value in 'HH:MM:SS' format.
    """
    try:
        # Initialize an empty dictionary to store the results
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Initialize the average handling time as zero
            average_handling_time = "00:00:00"

            # Compute the total wrapup time
            wrapup_time = sql['wrapup_time'].sum()

            # Compute the total call duration
            call_duration = sql['call_duration'].sum()

            # Count the number of call duration entries
            call_duration_count = sql['call_duration'].count()

            # Compute the average handling time if there are call duration entries
            if call_duration_count > 0:
                # Calculate the average handling time in seconds
                average_handling_time_seconds = (wrapup_time + call_duration) / call_duration_count

                # Convert the average handling time from seconds to 'HH:MM:SS' format
                average_handling_time = time.strftime('%H:%M:%S', time.gmtime(average_handling_time_seconds))
        else:
            # If the DataFrame is empty, set the average handling time to zero
            average_handling_time = "00:00:00"

        # Store the average handling time in the dictionary
        dictFinal['average_handling_time'] = average_handling_time

        # Return the dictionary with the average handling time
        return dictFinal

    except Exception as err:
        # Print the traceback of the exception for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Optionally, return an empty dictionary or handle the exception as needed
        return {}


def average_wait_time(sql):
    """
    Computes the average wait time for live and historical data from a DataFrame.

    Args:
    - sql (pd.DataFrame): DataFrame containing the 'wait_time' column to compute the average wait time.

    Returns:
    - dict: A dictionary with the key 'average_wait_time' and its computed value in 'HH:MM:SS' format.
    """
    try:
        # Initialize an empty dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Initialize the average wait time as zero
            average_wait_time = "00:00:00"

            # Compute the total wait time
            Wait_Time = sql['wait_time'].sum()

            # Count the number of wait time entries
            wait_time_count = sql['wait_time'].count()

            # Compute the average wait time if there are wait time entries
            if wait_time_count > 0:
                # Calculate the average wait time in seconds
                average_wait_time_seconds = Wait_Time / wait_time_count

                # Convert the average wait time from seconds to 'HH:MM:SS' format
                average_wait_time = time.strftime('%H:%M:%S', time.gmtime(average_wait_time_seconds))
        else:
            # If the DataFrame is empty, set the average wait time to zero
            average_wait_time = "00:00:00"

        # Store the average wait time in the dictionary
        dictFinal['average_wait_time'] = average_wait_time

        # Return the dictionary with the average wait time
        return dictFinal

    except Exception as err:
        # Print the traceback of the exception for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Optionally, return an empty dictionary or handle the exception as needed
        return {}


def average_wrapup_time(sql):
    """
    Computes the average wrap-up time for live and historical data from a DataFrame.

    Args:
    - sql (pd.DataFrame): DataFrame containing the 'wrapup_time' and 'call_status_disposition' columns.

    Returns:
    - dict: A dictionary with the key 'average_wrapup_time' and its computed value in 'HH:MM:SS' format.
    """
    try:
        # Initialize an empty dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Initialize the average wrap-up time as zero
            average_wrapup_time = "00:00:00"

            # Compute the total wrap-up time
            Wrapup_time = sql['wrapup_time'].sum()

            # Filter the DataFrame to include only rows where 'call_status_disposition' is 'answered'
            sql = sql[sql.call_status_disposition == 'answered']

            # Count the number of wrap-up time entries
            wrapup_time_count = sql['wrapup_time'].count()

            # Compute the average wrap-up time if there are wrap-up time entries
            if wrapup_time_count > 0:
                # Calculate the average wrap-up time in seconds
                average_wrapup_time_seconds = Wrapup_time / wrapup_time_count

                # Convert the average wrap-up time from seconds to 'HH:MM:SS' format
                average_wrapup_time = time.strftime('%H:%M:%S', time.gmtime(average_wrapup_time_seconds))
        else:
            # If the DataFrame is empty, set the average wrap-up time to zero
            average_wrapup_time = "00:00:00"

        # Store the average wrap-up time in the dictionary
        dictFinal['average_wrapup_time'] = average_wrapup_time

        # Return the dictionary with the average wrap-up time
        return dictFinal

    except Exception as err:
        # Print the traceback of the exception for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Optionally, return an empty dictionary or handle the exception as needed
        return {}


def average_call_duration(sql):
    """
    Computes the average call duration for live and historical data from a DataFrame.

    Args:
    - sql (pd.DataFrame): DataFrame containing 'call_duration' and 'call_status_disposition' columns.

    Returns:
    - dict: A dictionary with the key 'average_call_duration' and its computed value in 'HH:MM:SS' format.
    """
    try:
        # Initialize an empty dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Initialize the average call duration as zero
            average_call_duration = "00:00:00"

            # Compute the total call duration
            Call_Duration = sql['call_duration'].sum()

            # Filter the DataFrame to include only rows where 'call_status_disposition' is 'answered'
            call_duration_count_ans = sql[sql.call_status_disposition == 'answered']

            # Count the number of answered calls
            if not call_duration_count_ans.empty:
                call_duration_count = call_duration_count_ans['call_status_disposition'].count()
            else:
                call_duration_count = 0

            # Compute the average call duration if there are answered calls
            if call_duration_count > 0:
                # Calculate the average call duration in seconds
                average_call_duration_seconds = Call_Duration / call_duration_count

                # Convert the average call duration from seconds to 'HH:MM:SS' format
                average_call_duration = time.strftime('%H:%M:%S', time.gmtime(average_call_duration_seconds))
        else:
            # If the DataFrame is empty, set the average call duration to zero
            average_call_duration = "00:00:00"

        # Store the average call duration in the dictionary
        dictFinal['average_call_duration'] = average_call_duration

        # Return the dictionary with the average call duration
        return dictFinal

    except Exception as err:
        # Print the traceback of the exception for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Optionally, return an empty dictionary or handle the exception as needed
        return {}

def abandon_rate(sql):
    """
    Computes the abandon rate for live and historical data from a DataFrame.

    Args:
    - sql (pd.DataFrame): DataFrame containing 'call_status_disposition' column.

    Returns:
    - dict: A dictionary with the key 'abandon_rate' and its computed value as a percentage.
    """
    try:
        # Initialize an empty dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Initialize the abandon rate to zero
            abandon_rate = 0

            # Filter the DataFrame to include only rows where 'call_status_disposition' is 'abandon'
            TotalAbandonCallDis = sql[sql.call_status_disposition == 'abandon']

            # Count the number of abandoned calls
            if not TotalAbandonCallDis.empty:
                TotalAbandonCall = TotalAbandonCallDis['call_status_disposition'].count()
            else:
                TotalAbandonCall = 0

            # Count the total number of calls
            TotalcallDis = sql['call_status_disposition'].count()

            # Compute the abandon rate if there are calls
            if TotalcallDis > 0:
                # Calculate the abandon rate as a percentage
                abandon_rate = (TotalAbandonCall / TotalcallDis) * 100

                # Round the abandon rate to 2 decimal places
                abandon_rate = round(abandon_rate, 2)
        else:
            # If the DataFrame is empty, set the abandon rate to zero
            abandon_rate = 0

        # Store the abandon rate in the dictionary
        dictFinal['abandon_rate'] = abandon_rate

        # Return the dictionary with the abandon rate
        return dictFinal

    except Exception as err:
        # Print the traceback of the exception for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Optionally, return an empty dictionary or handle the exception as needed
        return {}


def call_back_Scheduled(sql):
    """
    Computes the number of scheduled callbacks from a DataFrame.

    Args:
    - sql (pd.DataFrame): DataFrame containing 'next_call_time' column.

    Returns:
    - dict: A dictionary with the key 'next_call_time' and its computed value.
    """
    try:
        # Initialize an empty dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter the DataFrame to include only rows where 'next_call_time' is not 0
            call_back_scheduled = sql[sql.next_call_time != 0]

            # Count the number of rows where 'next_call_time' is not 0
            next_call_time = call_back_scheduled['next_call_time'].count()
        else:
            # If the DataFrame is empty, set the number of next call times to zero
            next_call_time = 0

        # Store the count of next call times in the dictionary
        dictFinal['next_call_time'] = next_call_time

        # Return the dictionary with the number of scheduled callbacks
        return dictFinal

    except Exception as err:
        # Print the traceback of the exception for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Optionally, return an empty dictionary or handle the exception as needed
        return {}


def total_answered_call(sql):
    """
    Computes the total number of answered calls from a DataFrame.

    Args:
    - sql (pd.DataFrame): DataFrame containing 'call_status_disposition' column.

    Returns:
    - dict: A dictionary with the key 'total_answered_call' and its computed value.
    """
    try:
        # Initialize an empty dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter the DataFrame to include only rows where 'call_status_disposition' is 'answered'
            TotalAnsCall = sql[sql.call_status_disposition == 'answered']

            # Count the number of rows where 'call_status_disposition' is 'answered'
            TotalAnsCall = len(TotalAnsCall)
        else:
            # If the DataFrame is empty, set the total answered calls to zero
            TotalAnsCall = 0

        # Store the count of answered calls in the dictionary
        dictFinal['total_answered_call'] = TotalAnsCall

        # Return the dictionary with the total number of answered calls
        return dictFinal

    except Exception as err:
        # Print the traceback of the exception for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Optionally, return an empty dictionary or handle the exception as needed
        return {}


def average_queue_time(sql):
    """
    Computes the average queue time for live and historical data.

    Args:
    - sql (pd.DataFrame): DataFrame containing 'q_enter_time' and 'q_leave_time' columns.

    Returns:
    - dict: A dictionary with the key 'average_queue_time' and its computed value.
    """
    try:
        # Initialize an empty dictionary to store the result
        dictFinal = {}
        # Initialize average_queue_call to 0
        average_queue_call = 0

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter out rows with invalid queue times
            sql = sql.loc[(sql['q_enter_time'] != '0000-00-00 00:00:00') & (sql['q_leave_time'] != '0000-00-00 00:00:00')]

            # Convert 'q_enter_time' and 'q_leave_time' to datetime format
            sql['q_enter_time'] = pd.to_datetime(sql['q_enter_time'])
            sql['q_leave_time'] = pd.to_datetime(sql['q_leave_time'])

            # Calculate the queue time in seconds
            sql['queue_time'] = (sql['q_leave_time'] - sql['q_enter_time']) / pd.Timedelta(seconds=1)

            # Check again if the DataFrame is not empty after filtering
            if not sql.empty:
                # Calculate the total number of rows
                dfLen = len(sql)
                # Sum of all queue times
                average_queue_call = sql['queue_time'].sum()
                # Compute the average queue time
                average_queue_call = average_queue_call / dfLen
                # Round the average queue time to the nearest integer
                average_queue_call = round(average_queue_call)

        # Store the average queue time in the dictionary
        dictFinal['average_queue_time'] = average_queue_call

        # Return the dictionary with the average queue time
        return dictFinal

    except Exception as err:
        # Print the traceback of the exception for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Optionally, return an empty dictionary or handle the exception as needed
        return {}


def inbound_abandon_within_and_after_20(sql):
    """
    Computes the count of inbound abandoned calls that were abandoned after and within 20 seconds.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition',
      'campaign_type', 'q_enter_time', and 'q_leave_time'.

    Returns:
    - dict: A dictionary with keys 'inbound_abandon_after_20' and 'inbound_abandon_within_20'
      representing the counts of abandoned calls after and within 20 seconds, respectively.
    """
    try:
        # Define the threshold time in seconds
        

        # Initialize a dictionary to store the result
        dictFinal = {}

        # Initialize counters for the results
        inbound_abandon_after_20 = 0
        inbound_abandon_within_20 = 0

        # Create a reference to the DataFrame
        df = sql

        # Check if the DataFrame is not empty
        if not df.empty:
            # Filter DataFrame for abandoned inbound calls
            df = sql.loc[(sql['call_status_disposition'] == 'abandon') & (sql['campaign_type'] == 'INBOUND')]

            # Further filter out rows with invalid queue times
            df = df.loc[(df['q_enter_time'] != '0000-00-00 00:00:00') & (df['q_leave_time'] != '0000-00-00 00:00:00')]

            # Convert queue times to datetime format
            df['q_enter_time'] = pd.to_datetime(df['q_enter_time'])
            df['q_leave_time'] = pd.to_datetime(df['q_leave_time'])

            # Calculate the queue time in seconds
            df['inbound_abandon_with_and_after_20'] = (df['q_leave_time'] - df['q_enter_time']) / pd.Timedelta(seconds=1)

            # Convert the calculated queue times to integers
            df1 = df.astype({"inbound_abandon_with_and_after_20": int})

            # Check if the DataFrame is not empty after processing
            if not df1.empty:
                # Count of abandoned calls after 20 seconds
                df2 = df[df1['inbound_abandon_with_and_after_20'] >= Threshold]
                inbound_abandon_after_20 = len(df2)

                # Count of abandoned calls within 20 seconds
                df3 = df[df1['inbound_abandon_with_and_after_20'] < Threshold]
                inbound_abandon_within_20 = len(df3)

        # Store the results in the dictionary
        dictFinal['inbound_abandon_after_20'] = inbound_abandon_after_20
        dictFinal['inbound_abandon_within_20'] = inbound_abandon_within_20

        # Return the dictionary containing the results
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def inbound_answered_within_and_after_20(sql):
    """
    Computes the count of inbound answered calls that were answered after and within 20 seconds.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition',
      'campaign_type', 'q_enter_time', and 'q_leave_time'.

    Returns:
    - dict: A dictionary with keys 'inbound_answered_after_20' and 'inbound_answered_within_20'
      representing the counts of answered calls after and within 20 seconds, respectively.
    """
    try:
        # Define the threshold time in seconds
        

        # Initialize a dictionary to store the result
        dictFinal = {}

        # Initialize counters for the results
        inbound_answered_after_20 = 0
        inbound_answered_within_20 = 0

        # Create a reference to the DataFrame
        df = sql

        # Check if the DataFrame is not empty
        if not df.empty:
            # Filter DataFrame for answered inbound calls
            df = sql.loc[(sql['call_status_disposition'] == 'answered') & (sql['campaign_type'] == 'INBOUND')]

            # Further filter out rows with invalid queue times
            df = df.loc[(df['q_enter_time'] != '0000-00-00 00:00:00') & (df['q_leave_time'] != '0000-00-00 00:00:00')]

            # Convert queue times to datetime format
            df['q_enter_time'] = pd.to_datetime(df['q_enter_time'])
            df['q_leave_time'] = pd.to_datetime(df['q_leave_time'])

            # Calculate the queue time in seconds
            df['inbound_answered_within_and_after_20'] = (df['q_leave_time'] - df['q_enter_time']) / pd.Timedelta(seconds=1)

            # Convert the calculated queue times to integers
            df1 = df.astype({"inbound_answered_within_and_after_20": int})

            # Check if the DataFrame is not empty after processing
            if not df1.empty:
                # Count of answered calls after 20 seconds
                df2 = df1[df1['inbound_answered_within_and_after_20'] >= Threshold]
                inbound_answered_after_20 = len(df2)

                # Count of answered calls within 20 seconds
                df3 = df1[df1['inbound_answered_within_and_after_20'] < Threshold]
                inbound_answered_within_20 = len(df3)

        # Store the results in the dictionary
        dictFinal['inbound_answered_after_20'] = inbound_answered_after_20
        dictFinal['inbound_answered_within_20'] = inbound_answered_within_20

        # Return the dictionary containing the results
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def inbound_answered_call(sql):
    """
    Computes the total count of inbound answered calls.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition' and 'campaign_type'.

    Returns:
    - dict: A dictionary with the key 'inbound_answered_call' representing the count of inbound answered calls.
    """
    try:
        # Initialize a dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter DataFrame for answered inbound calls
            sql = sql.loc[(sql['call_status_disposition'] == 'answered') & (sql['campaign_type'] == 'INBOUND')]

            # Count the number of inbound answered calls
            inbound_answered_call = sql['campaign_type'].count()
        else:
            # Set the count to 0 if the DataFrame is empty
            inbound_answered_call = 0

        # Store the result in the dictionary
        dictFinal['inbound_answered_call'] = inbound_answered_call

        # Return the dictionary containing the result
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}



def inbound_call_abandon(sql):
    """
    Computes the total count of inbound call abandonments.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition' and 'campaign_type'.

    Returns:
    - dict: A dictionary with the key 'inbound_call_abandon' representing the count of inbound call abandonments.
    """
    try:
        # Initialize a dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter DataFrame for abandoned inbound calls
            sql = sql.loc[(sql['call_status_disposition'] == 'abandon') & (sql['campaign_type'] == 'INBOUND')]

            # Count the number of inbound call abandonments
            inbound_call_abandon = sql['campaign_type'].count()
        else:
            # Set the count to 0 if the DataFrame is empty
            inbound_call_abandon = 0

        # Store the result in the dictionary
        dictFinal['inbound_call_abandon'] = inbound_call_abandon

        # Return the dictionary containing the result
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}

def outbound_answered_within_and_after_20(sql):
    """
    Computes the count of outbound answered calls within and after 20 seconds.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition', 'campaign_type', and 'call_duration'.

    Returns:
    - dict: A dictionary with keys 'outbound_answered_after_20' and 'outbound_answered_within_20' representing the counts of outbound answered calls based on the call duration.
    """
    try:
        # Define the threshold for call duration (in seconds)
        

        # Initialize a dictionary to store the result
        dictFinal = {}

        # Initialize counters for the two categories
        outbound_answered_after_20 = 0
        outbound_answered_within_20 = 0

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter the DataFrame for outbound answered calls
            df = sql.loc[(sql['call_status_disposition'] == 'answered') & (sql['campaign_type'] == 'OUTBOUND')]

            # Count outbound answered calls with duration greater than the threshold
            outbound_answered_after_20 = len(df[df['call_duration'] > Threshold])

            # Count outbound answered calls with duration less than the threshold
            outbound_answered_within_20 = len(df[df['call_duration'] < Threshold])

        # Store the results in the dictionary
        dictFinal['outbound_answered_after_20'] = outbound_answered_after_20
        dictFinal['outbound_answered_within_20'] = outbound_answered_within_20

        # Return the dictionary containing the results
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def outbound_disconnected_within_and_after_20(sql):
    """
    Computes the percentage of successfully answered and failed calls for outbound calls based on call status.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition'.

    Returns:
    - dict: A dictionary with 'success_percentage' and 'failure_percentage' representing the percentages of answered and non-answered calls.
    """
    try:
        # Initialize a dictionary to store the result
        dictFinal = {}

        # Filter the DataFrame for answered calls
        tmp_answered = sql.loc[(sql['call_status_disposition'] == 'answered')]
        number_of_call_ans = len(tmp_answered)

        # Filter the DataFrame for non-answered calls
        unanswered = sql.loc[(sql['call_status_disposition'] != 'answered')]
        number_of_call_uns = len(unanswered)

        # Calculate the success percentage if there are any calls
        if number_of_call_ans + number_of_call_uns > 0:
            success_percentage = (number_of_call_ans / (number_of_call_uns + number_of_call_ans)) * 100
            success_percentage = round(success_percentage)
        else:
            success_percentage = 0

        # Calculate the failure percentage if there are any calls
        if number_of_call_ans + number_of_call_uns > 0:
            failure_percentage = (number_of_call_uns / (number_of_call_ans + number_of_call_uns)) * 100
            failure_percentage = round(failure_percentage)
        else:
            failure_percentage = 0

        # Store the results in the dictionary
        dictFinal['success_percentage'] = success_percentage
        dictFinal['failure_percentage'] = failure_percentage

        # Return the dictionary containing the results
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}

def outbound_answered_call(sql):
    """
    Computes the total number of outbound calls that were answered.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition' and 'campaign_type'.

    Returns:
    - dict: A dictionary with the count of outbound answered calls.
    """
    try:
        # Initialize a dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter the DataFrame for outbound answered calls
            sql = sql.loc[(sql['call_status_disposition'] == 'answered') & (sql['campaign_type'] == 'OUTBOUND')]
            # Count the number of outbound answered calls
            outbound_answered_call = len(sql)
        else:
            # If the DataFrame is empty, set the count to 0
            outbound_answered_call = 0

        # Store the result in the dictionary
        dictFinal['outbound_answered_call'] = outbound_answered_call

        # Return the dictionary containing the result
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def outbound_call_busy(sql):
    """
    Computes the total number of outbound calls that were busy.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition' and 'campaign_type'.

    Returns:
    - dict: A dictionary with the count of outbound busy calls.
    """
    try:
        # Initialize a dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter the DataFrame for outbound busy calls
            sql = sql.loc[(sql['call_status_disposition'] == 'busy') & (sql['campaign_type'] == 'OUTBOUND')]
            # Count the number of outbound busy calls
            outbound_call_busy = len(sql)
        else:
            # If the DataFrame is empty, set the count to 0
            outbound_call_busy = 0

        # Store the result in the dictionary
        dictFinal['outbound_call_busy'] = outbound_call_busy

        # Return the dictionary containing the result
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def outbound_call_disconnected(sql):
    """
    Computes the total number of outbound calls that were disconnected.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition' and 'campaign_type'.

    Returns:
    - dict: A dictionary with the count of outbound disconnected calls.
    """
    try:
        # Initialize a dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter the DataFrame for outbound disconnected calls
            sql = sql.loc[(sql['call_status_disposition'] == 'DC') & (sql['campaign_type'] == 'OUTBOUND')]
            # Count the number of outbound disconnected calls
            outbound_call_disconnected = len(sql)
        else:
            # If the DataFrame is empty, set the count to 0
            outbound_call_disconnected = 0

        # Store the result in the dictionary
        dictFinal['outbound_call_disconnected'] = outbound_call_disconnected

        # Return the dictionary containing the result
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def outbound_call_no_answered(sql):
    """
    Computes the total number of outbound calls that were not answered.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition' and 'campaign_type'.

    Returns:
    - dict: A dictionary with the count of outbound calls that were not answered.
    """
    try:
        # Initialize a dictionary to store the result
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter the DataFrame for outbound calls with no answer
            sql = sql.loc[(sql['call_status_disposition'] == 'noans') & (sql['campaign_type'] == 'OUTBOUND')]
            # Count the number of outbound calls with no answer
            outbound_call_no_answered = len(sql)
        else:
            # If the DataFrame is empty, set the count to 0
            outbound_call_no_answered = 0

        # Store the result in the dictionary
        dictFinal['outbound_call_no_answered'] = outbound_call_no_answered

        # Return the dictionary containing the result
        return dictFinal

    except Exception as err:
        # Print the traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def SLA(sql):
    """
    Compute the Service Level Agreement (SLA) for inbound calls, both answered and abandoned, based on the given threshold.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'campaign_type', 'call_status_disposition', 'q_enter_time', and 'q_leave_time'.

    Returns:
    - dict: A dictionary with the SLA percentage.
    """
    try:
        # Define the SLA threshold in seconds
        

        # Initialize dictionaries and counters
        sla_dict = {}
        dictFinal = {}
        inbound_call_count = 0
        ans_sla = 0

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter for inbound calls
            lenSql = sql[sql.campaign_type == 'INBOUND']
            # Count the total number of inbound calls
            inbound_call_count = len(lenSql)

            # Filter for answered inbound calls
            df = sql.loc[(sql['call_status_disposition'] == 'answered') & (sql['campaign_type'] == 'INBOUND')]
            # Ensure q_enter_time and q_leave_time are valid
            df = df.loc[(df['q_enter_time'] != '0000-00-00 00:00:00') & (df['q_leave_time'] != '0000-00-00 00:00:00')]
            # Convert times to datetime
            df['q_enter_time'] = pd.to_datetime(df['q_enter_time'])
            df['q_leave_time'] = pd.to_datetime(df['q_leave_time'])
            # Calculate the difference in seconds
            df['ans_sla_diff'] = (df.q_leave_time - df.q_enter_time) / pd.Timedelta(seconds=1)
            # Convert SLA differences to integer
            df1 = df.astype({"ans_sla_diff": int})
            # Count the number of calls within the SLA threshold
            if not df1.empty:
                df2 = df1[df1.ans_sla_diff < Threshold]
                if not df2.empty:
                    ans_sla = df2['ans_sla_diff'].count()

        # Initialize abandon_sla
        abandon_sla = 0
        dfa = sql
        # Filter for abandoned inbound calls
        if not dfa.empty:
            dfa = sql.loc[(sql['call_status_disposition'] == 'abandon') & (sql['campaign_type'] == 'INBOUND')]
            # Ensure q_enter_time and q_leave_time are valid
            dfa = dfa.loc[(dfa['q_enter_time'] != '0000-00-00 00:00:00') & (dfa['q_leave_time'] != '0000-00-00 00:00:00')]
            # Convert times to datetime
            dfa['q_enter_time'] = pd.to_datetime(dfa['q_enter_time'])
            dfa['q_leave_time'] = pd.to_datetime(dfa['q_leave_time'])
            # Calculate the difference in seconds
            dfa['abandon_sla_diff'] = (dfa.q_leave_time - dfa.q_enter_time) / pd.Timedelta(seconds=1)
            # Convert SLA differences to integer
            df1 = dfa.astype({"abandon_sla_diff": int})
            # Count the number of abandoned calls within the SLA threshold
            if not df1.empty:
                df3 = df1[df1.abandon_sla_diff < Threshold]
                if not df3.empty:
                    abandon_sla = df3['abandon_sla_diff'].count()

        # Calculate SLA percentage
        if inbound_call_count > 0:
            sla = ((ans_sla + abandon_sla) / inbound_call_count) * 100
        else:
            sla = 0

        # Round SLA to integer
        sla = int(sla)

        # Store SLA result in dictionary
        sla_dict[inbound_call_count] = sla
        dictFinal['sla'] = sla

        return dictFinal

    except Exception as err:
        # Print traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def call_status_disposition(sql):
    """
    Compute the count of each call status disposition for live and historical data.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with a 'call_status_disposition' column.

    Returns:
    - dict: A dictionary with call status dispositions as keys and their counts as values.
    """
    try:
        # Initialize the final result dictionary
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Group by 'call_status_disposition' and count occurrences
            CallStatusDis = sql.groupby('call_status_disposition', dropna=False, observed=True)['call_status_disposition'].count()
            # Convert the Series to a dictionary
            call_status_disposition = CallStatusDis.to_dict()
        else:
            # Set the result to 0 if DataFrame is empty
            call_status_disposition = 0

        # Store the result in the dictionary
        dictFinal['call_status_disposition'] = call_status_disposition

        # Return the dictionary with the call status dispositions
        return dictFinal

    except Exception as err:
        # Print traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def aht_agentwise(sql):
    """
    Compute average handling time (AHT) for agents and return the top 10 agents with the highest AHT.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition', 'agent_id', 'wrapup_time', and 'call_duration'.

    Returns:
    - dict: A dictionary with lists of agent IDs, their AHT values, and their call volumes.
    """
    try:
        # Initialize lists to hold agent IDs, AHT values, and call volumes
        agent_id_list, agent_aht_list, agent_call_volume = [], [], []

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter the DataFrame to include only answered calls and valid agent IDs
            df = sql.loc[(sql['call_status_disposition'] == 'answered') & (sql['agent_id'] != 0)]

            # Calculate the total time spent on calls (wrapup time + call duration)
            df["wrapandcallsum"] = df["wrapup_time"] + df["call_duration"]

            # Convert the calculated time to integer type
            df = df.astype({"wrapandcallsum": int})

            # Group by 'agent_id' and calculate the mean wrapup time and call count
            top_aht_agent = df.groupby('agent_id', dropna=False, observed=True).agg({
                'wrapandcallsum': 'mean',   # Calculate the average handling time
                'call_status_disposition': 'count'  # Count the number of calls
            }).reset_index()

            # Round the average handling time to 2 decimal places
            top_aht_agent['wrapandcallsum'] = top_aht_agent['wrapandcallsum'].round(2)

            # Sort the agents by AHT in descending order and get the top 10 agents
            top_aht_agent = top_aht_agent.sort_values(by=['wrapandcallsum'], ascending=False)
            top_aht_agent = top_aht_agent.head(10)

            # Extract the lists of agent IDs, AHT values, and call volumes
            agent_id_list = top_aht_agent['agent_id'].tolist()
            agent_aht_list = top_aht_agent['wrapandcallsum'].tolist()
            agent_call_volume = top_aht_agent['call_status_disposition'].tolist()

            # Prepare the result dictionary
            dictFinal = {
                "agent_id_list": agent_id_list,
                "agent_aht_list": agent_aht_list,
                "agent_call_volume": agent_call_volume
            }
        else:
            # Return empty lists if the DataFrame is empty
            dictFinal = {
                "agent_id_list": agent_id_list,
                "agent_aht_list": agent_aht_list,
                "agent_call_volume": agent_call_volume
            }

        return dictFinal

    except Exception as err:
        # Print traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def aht_and_call_volume(sql):
    """
    Compute average handling time (AHT) and call volume for each hour of the day from live and historical data.

    Args:
    - sql (pd.DataFrame): DataFrame containing call data with columns 'call_status_disposition', 'wrapup_time',
                          'call_duration', and 'call_start_date_time'.

    Returns:
    - dict: A dictionary with lists of hours, AHT values, and call volumes.
    """
    try:
        # Initialize lists to hold hours, AHT values, and call volumes
        tmp_hour_list, aht_value_list, call_volue_list = [], [], []

        # Check if the DataFrame is not empty
        if not sql.empty:
            # Filter the DataFrame to include only answered calls
            df = sql[sql.call_status_disposition == 'answered']

            # Calculate the total handling time (wrapup time + call duration)
            df["wrapandcallsum"] = df['wrapup_time'] + df['call_duration']

            # Convert the calculated time to integer type
            df = df.astype({"wrapandcallsum": int})

            # Extract the hour from 'call_start_date_time'
            df['time_hour'] = pd.to_datetime(df['call_start_date_time']).dt.hour

            # Create a list of unique hours from the DataFrame
            test_list = df['time_hour'].tolist()
            res = []
            [res.append(x) for x in test_list if x not in res]

            # Group by hour and calculate AHT and call volume
            aht_hour = df.groupby('time_hour', dropna=False, observed=True).agg({
                'wrapandcallsum': 'mean',  # Calculate average handling time
                'call_status_disposition': 'count'  # Count number of calls
            }).reset_index()

            # Round AHT to 2 decimal places
            aht_hour['wrapandcallsum'] = aht_hour['wrapandcallsum'].round(2)

            # Format hours as two-digit strings
            aht_hour['time_hour'] = aht_hour['time_hour'].astype(str).str.zfill(2)

            # Create a list of all hours in 24-hour format
            hour_list = [str(tmp_hour).zfill(2) for tmp_hour in range(24)]

            # Process each hour and aggregate data
            for hour in hour_list:
                aht_hour_df = aht_hour[aht_hour['time_hour'] == hour]
                if not aht_hour_df.empty:
                    for index, row in aht_hour_df.iterrows():
                        hour = row['time_hour']
                        aht = row['wrapandcallsum']
                        call_volume = row['call_status_disposition']
                        tmp_hour_list.append(hour)
                        aht_value_list.append(aht)
                        call_volue_list.append(call_volume)
                else:
                    # If no data for the hour, append zeros
                    tmp_hour_list.append(hour)
                    aht_value_list.append(0)
                    call_volue_list.append(0)

        # Prepare the result dictionary
        dictFinal = {
            "hour_list": tmp_hour_list,
            "aht_value_list": aht_value_list,
            "call_volue_list": call_volue_list
        }

        return dictFinal

    except Exception as err:
        # Print traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def agent_ideal_time(agent_live_df):
    """
    Compute the ideal time for agents who are currently in a 'FREE' state.

    Args:
    - agent_live_df (pd.DataFrame): DataFrame containing agent data with columns 'agent_state' and 'last_activity_time'.

    Returns:
    - dict: A dictionary containing the ideal time for agents in the 'FREE' state.
    """
    try:
        # Load the DataFrame and initialize timezone and current time
        AgentInCall = agent_live_df
        original = timezone('Asia/Kolkata')
        CurrentTime = datetime.now(original)
        CurrentTime = CurrentTime.strftime("%Y-%m-%d %H:%M:%S")
        dictFinal = {}

        if not AgentInCall.empty:
            # Convert agent state column to JSON and then back to a list
            agentStateFree = AgentInCall['agent_state'].to_json(orient='records')
            agentStateFree = json.loads(agentStateFree)

            # Initialize the ideal time to "00:00:00"
            dictFinal['agent_ideal_time'] = "00:00:00"

            # Check for agents in 'FREE' state
            if 'FREE' in agentStateFree:
                df = AgentInCall[AgentInCall.agent_state == 'FREE']
                df = df[df.last_activity_time != '0000-00-00 00:00:00']

                if not df.empty:
                    # Convert 'last_activity_time' to datetime and calculate time difference
                    df['last_activity_time'] = pd.to_datetime(df['last_activity_time'])
                    df['unix_timestamp'] = pd.to_datetime(CurrentTime)
                    df['Agent_diff'] = (df['unix_timestamp'] - df['last_activity_time']) / pd.Timedelta(seconds=1)
                    df1 = df.astype({"Agent_diff": int})

                    # Calculate the maximum ideal time from the time differences
                    AID = df['Agent_diff'].max()
                    AgentIdealTime = time.strftime('%H:%M:%S', time.gmtime(AID))
                    dictFinal['agent_ideal_time'] = AgentIdealTime

        return dictFinal

    except Exception as err:
        # Print traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def total_agent_manual_outbound(agent_live_df):
    """
    Compute the total number of agents handling manual outbound calls for live data.

    Args:
    - agent_live_df (pd.DataFrame): DataFrame containing agent data with columns 'agent_state' and 'dialer_type'.

    Returns:
    - dict: A dictionary containing the total count of agents handling manual outbound calls.
    """
    try:
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not agent_live_df.empty:
            # Filter the DataFrame for agents in 'INCALL' state with 'PREVIEW' dialer type
            filtered_df = agent_live_df[(agent_live_df['agent_state'] == 'INCALL') & (agent_live_df['dialer_type'] == 'PREVIEW')]

            # Count the number of rows in the filtered DataFrame
            total_agents = len(filtered_df)
        else:
            # If the DataFrame is empty, set count to 0
            total_agents = 0

        # Add the count to the result dictionary
        dictFinal['total_agent_manual_outbound'] = total_agents

        return dictFinal

    except Exception as err:
        # Print traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def total_agent_progressive_inbound(agent_live_df):
    """
    Compute the total number of agents handling progressive inbound calls for live data.

    Args:
    - agent_live_df (pd.DataFrame): DataFrame containing agent data with columns 'agent_state' and 'dialer_type'.

    Returns:
    - dict: A dictionary containing the total count of agents handling progressive inbound calls.
    """
    try:
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not agent_live_df.empty:
            # Filter the DataFrame for agents in 'INCALL' state with 'PROGRESSIVE' dialer type
            filtered_df = agent_live_df[(agent_live_df['agent_state'] == 'INCALL') & (agent_live_df['dialer_type'] == 'PROGRESSIVE')]

            # Count the number of rows in the filtered DataFrame
            total_agents = len(filtered_df)
        else:
            # If the DataFrame is empty, set count to 0
            total_agents = 0

        # Add the count to the result dictionary
        dictFinal['total_agent_progressive_inbound'] = total_agents

        return dictFinal

    except Exception as err:
        # Print traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}

def total_agent_predictive(agent_live_df):
    """
    Compute the total number of agents handling predictive calls for live data.

    Args:
    - agent_live_df (pd.DataFrame): DataFrame containing agent data with columns 'agent_state' and 'campaign_type'.

    Returns:
    - dict: A dictionary containing the total count of agents handling predictive calls.
    """
    try:
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not agent_live_df.empty:
            # Filter the DataFrame for agents in 'INCALL' state with campaign_type '8196'
            filtered_df = agent_live_df[(agent_live_df['agent_state'] == 'INCALL') & (agent_live_df['campaign_type'] == '8196')]

            # Count the number of rows in the filtered DataFrame
            total_agents = len(filtered_df)
        else:
            # If the DataFrame is empty, set count to 0
            total_agents = 0

        # Add the count to the result dictionary
        dictFinal['total_agent_predictive'] = total_agents

        return dictFinal

    except Exception as err:
        # Print traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}

def agent_live(agent_live_df):
    """
    Compute the current state of agents for live data.

    Args:
    - agent_live_df (pd.DataFrame): DataFrame containing agent data with columns 'closer_time' and 'agent_state'.

    Returns:
    - dict: A dictionary with counts of agents in different states.
    """
    try:
        dictFinal = {}

        # Check if the DataFrame is not empty
        if not agent_live_df.empty:
            # Group by 'closer_time' and 'agent_state' and count the occurrences
            agent_live_grouped = agent_live_df.groupby(['closer_time', 'agent_state'], dropna=False, observed=True).size().reset_index(name='count')

            # Total number of agents
            total_agent_count = len(agent_live_df)

            # Initialize agent state counts
            dictFinal['agent_away'] = 0
            dictFinal['agent_available'] = 0
            dictFinal['agent_busy'] = 0
            dictFinal['agent_after_call_work'] = 0

            # Process the grouped DataFrame
            if not agent_live_grouped.empty:
                agent_live_list = agent_live_grouped.to_dict(orient='records')

                for agent in agent_live_list:
                    agent_state = agent['agent_state']
                    closer_time = agent['closer_time']
                    count = agent['count']

                    # Update counts based on agent state and closer_time
                    if agent_state == 'CLOSURE' and closer_time == -999:
                        dictFinal['agent_away'] = count
                    elif agent_state == 'FREE':
                        dictFinal['agent_available'] = count
                    elif agent_state == 'INCALL':
                        dictFinal['agent_busy'] = count
                    elif agent_state == 'CLOSURE' and closer_time != -999:
                        dictFinal['agent_after_call_work'] += count

            # Update total agent count
            dictFinal['agent_total'] = total_agent_count

        else:
            # If the DataFrame is empty, set all counts to 0
            dictFinal['agent_away'] = 0
            dictFinal['agent_available'] = 0
            dictFinal['agent_busy'] = 0
            dictFinal['agent_after_call_work'] = 0
            dictFinal['agent_total'] = 0

        return dictFinal

    except Exception as err:
        # Print traceback for debugging
        traceback.print_exc()

        # Log the error message
        log.error(str(err))

        # Return an empty dictionary or handle the exception as needed
        return {}


def call_in_queue(agent_live_df):
    """
    Compute the details of calls currently in the queue, including phone numbers and queue times, for live data.

    Args:
    - agent_live_df (pd.DataFrame): DataFrame containing queue data with columns 'q_enter_time' and 'cust_ph_no'.

    Returns:
    - dict: A dictionary with lists of phone numbers and their corresponding queue times.
    """
    try:
        # Initialize lists for phone numbers and queue times
        phone_no_list = []
        queue_time_list = []

        # Define the time zone and get the current time
        original = timezone('Asia/Kolkata')
        current_time = datetime.now(original)
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # Remove duplicate rows
        agent_live_df.drop_duplicates(inplace=True)

        if not agent_live_df.empty and 'cust_ph_no' in agent_live_df.columns:
            # Extract relevant columns
            q_enter_time_and_cust_ph_no = agent_live_df[['q_enter_time', 'cust_ph_no']].copy()

            # Mask phone numbers
            def mask_phone_number(ph_no):
                if len(ph_no) <= 5:
                    return "XXXXXXXX" + ph_no[-2:]
                else:
                    return ph_no[:2] + "XXXX" + ph_no[-4:]

            q_enter_time_and_cust_ph_no['phone_no'] = q_enter_time_and_cust_ph_no['cust_ph_no'].apply(mask_phone_number)
            q_enter_time_and_cust_ph_no['current_date_time'] = pd.to_datetime(current_time_str)
            q_enter_time_and_cust_ph_no['q_enter_time'] = pd.to_datetime(q_enter_time_and_cust_ph_no['q_enter_time'])
            q_enter_time_and_cust_ph_no['queue_time'] = (q_enter_time_and_cust_ph_no['current_date_time'] - q_enter_time_and_cust_ph_no['q_enter_time']) / pd.Timedelta(seconds=1)

            # Get the top 5 longest queue times
            call_in_queue_df = q_enter_time_and_cust_ph_no[['phone_no', 'queue_time']]
            call_in_queue_df = call_in_queue_df.nlargest(5, 'queue_time')

            phone_no_list = call_in_queue_df['phone_no'].tolist()
            queue_time_list = call_in_queue_df['queue_time'].tolist()

        dictFinal = {"phone_no_list": phone_no_list, "queue_time_list": queue_time_list}
        return dictFinal

    except Exception as err:
        traceback.print_exc()
        log.error(str(err))
        return {"phone_no_list": [], "queue_time_list": []}


def ivr_performance_report(IVRSql):
    """
    Compute IVR performance metrics for live and historical data.

    Args:
    - IVRSql (pd.DataFrame): DataFrame containing IVR data with columns 'duration' and 'CampaignTransfer'.

    Returns:
    - dict: A dictionary with IVR performance metrics.
    """
    try:
        # Initialize the final dictionary
        dictFinal = {}
        ivrArr = {}

        if not IVRSql.empty:
            # Metrics Calculation
            # Exception: Duration <= 2 and no campaign transfer
            duration_exceptions = IVRSql[(IVRSql['duration'] <= 2) & (IVRSql['CampaignTransfer'] == "")]
            exception = duration_exceptions.shape[0]

            # IVR Abandoned: Duration > 2 and no campaign transfer
            duration_abandoned = IVRSql[(IVRSql['duration'] > 2) & (IVRSql['CampaignTransfer'] == "")]
            ivr_abandoned = duration_abandoned.shape[0]

            # Call to Agent: CampaignTransfer is not empty
            call_to_agent = IVRSql[IVRSql['CampaignTransfer'] != ""].shape[0]

        else:
            # Default values if DataFrame is empty
            exception = 0
            ivr_abandoned = 0
            call_to_agent = 0

        # Populate the results in the dictionary
        ivrArr['exception'] = exception
        ivrArr['ivr_abandoned'] = ivr_abandoned
        ivrArr['call_to_agent'] = call_to_agent
        dictFinal['ivrperformance'] = ivrArr

        return dictFinal

    except Exception as err:
        traceback.print_exc()
        log.error(str(err))
        return {"ivrperformance": {"exception": 0, "ivr_abandoned": 0, "call_to_agent": 0}}


def all_agent_list(selected_campaign_name):
    """
    Fetch agent_id list based on campaign and agent filter.

    Args:
        selected_campaign_name (str):
            Campaign name used for filtering agents.

        selected_agent_filter (str):
            If "ALL", return all agent_ids.
            Otherwise return agent_ids for the selected campaign.

    Returns:
        list:
            List of agent_id values.
    """

    try:
        # Create database connection
        mydb = sql_conn()

        # Check if user selected ALL agents
        '''if selected_agent_filter == "ALL":

            # Query to fetch all agents
            query = """
            SELECT agent_id, agent_name
            FROM agent
            """

        else:
            # Query to fetch agents for specific campaign
            query = f"""
            SELECT agent_id, agent_name
            FROM agent
            WHERE campaign_name = '{selected_campaign_name}'
            """'''

        #query = f"SELECT agent_id, agent_name FROM agent WHERE campaign_name = '{selected_campaign_name}'"
        query = f"SELECT a.agent_id, a.agent_name FROM agent a JOIN campaign c ON a.campaign_id = c.campaign_id WHERE c.campaign_name = '{selected_campaign_name}'"

        # Execute query and store result in DataFrame
        tmp_agent_id = pd.read_sql(query, con=mydb)

        # Convert agent_id column to Python list
        agent_id_list = tmp_agent_id['agent_id'].tolist()

        # Add "ALL" at the beginning of the list
        agent_id_list.insert(0, "ALL")

        # Return the list of agent IDs
        return agent_id_list

    except Exception as err:
        traceback.print_exc()
        log.error(str(err))
        return ["ALL"]


def get_skill_list_by_campaign(selected_campaign_name):
    """
    Fetch skill_id list based on campaign name.

    Args:
        selected_campaign_name (str): Campaign name used for filtering skill.

    Returns:
        list: List of skill_id values.
    """
    try:
        mydb = sql_conn()

        query = f"""
            SELECT a.skill_id,a.skill_name
            FROM skills a
            JOIN campaign c ON a.campaign_id = c.campaign_id
            WHERE c.campaign_name = '{selected_campaign_name}'
        """

        tmp_skill_df = pd.read_sql(query, con=mydb)

        skil_name_list = tmp_skill_df['skill_name'].tolist()

        skil_name_list.insert(0, "ALL")

        return skil_name_list

    except Exception as err:
        traceback.print_exc()
        log.error(str(err))
        return ["ALL"]

def get_list_name_by_campaign(selected_campaign_name):
    """
    Fetch list_name list based on campaign name.

    Args:
        selected_campaign_name (str): Campaign name used for filtering list.

    Returns:
        list: List of list_name values.
    """

    try:
        mydb = sql_conn()

        query = """
            SELECT a.list_id, a.list_name
            FROM list a
            JOIN campaign c ON a.campaign_id = c.campaign_id
            WHERE c.campaign_name = %s
        """

        tmp_list_df = pd.read_sql(query, con=mydb, params=[selected_campaign_name])

        list_name = tmp_list_df['list_name'].tolist()

        list_name.insert(0, "ALL")

        return list_name

    except Exception as err:
        traceback.print_exc()
        log.error(str(err))
        return ["ALL"]


def main_test(selected_campaign_name, start_date, end_date, selected_filter_name, selected_campaign_type, selected_agent_filter,selected_skills_name,selected_list_name):
    """
    Main function to compute various metrics based on selected parameters.

    Args:
    - selected_campaign_name (str): Name of the campaign.
    - start_date (str): Start date for data retrieval.
    - end_date (str): End date for data retrieval.
    - selected_filter_name (str): Filter criteria (e.g., "Today").
    - selected_campaign_type (str): Type of the campaign.

    Returns:
    - tuple: A tuple containing various metrics as dictionaries.
    """
    # Retrieve today's date
    today_date = get_date()

    # Check if the filter name is "Today"
    if selected_filter_name == "Today":
        # Establish a connection to the SQL database
        mydb = sql_conn()

        # Get the campaign ID for the selected campaign name
        campaign_id_value = get_campaign_id(mydb, selected_campaign_name)

        # Retrieve live data for agents and queues
        agent_live_df = agent_live_sql(mydb, campaign_id_value)
        agent_in_queue_df = QueueLiveSql(mydb, selected_campaign_name)

        # Read CSV files to get historical data
        df = read_csv_files(selected_campaign_name, start_date, end_date, today_date, selected_campaign_type, selected_agent_filter,selected_skills_name,selected_list_name)

        # If no data is retrieved, create an empty DataFrame with predefined columns
        if df is None:
            columns = ['agent_id', 'agent_name', 'campaign_id', 'campaign_name', 'wrapup_time', 'call_duration',
                       'wait_time', 'call_status_disposition', 'next_call_time', 'campaign_type', 'q_enter_time',
                       'q_leave_time', 'call_start_date_time', 'call_end_date_time']
            df = pd.DataFrame(columns=columns)

        # Calculate various metrics using the retrieved data
        average_handling_time_dict = average_handling_time(df)
        average_wait_time_dict = average_wait_time(df)
        average_wrapup_time_dict = average_wrapup_time(df)
        average_call_duration_dict = average_call_duration(df)
        abandon_rate_dict = abandon_rate(df)
        call_back_Scheduled_dict = call_back_Scheduled(df)
        total_answered_call_dict = total_answered_call(df)
        agent_ideal_time_dict = agent_ideal_time(agent_live_df)
        average_queue_time_dict = average_queue_time(df)
        inbound_abandon_within_and_after_20_dict = inbound_abandon_within_and_after_20(df)
        inbound_answered_within_and_after_20_dict = inbound_answered_within_and_after_20(df)

        # Calculate agent-specific metrics
        total_agent_manual_outbound_df = total_agent_manual_outbound(agent_live_df)
        total_agent_progressive_inbound_df = total_agent_progressive_inbound(agent_live_df)
        total_agent_predictive_df = total_agent_predictive(agent_live_df)

        # Calculate outbound call metrics
        outbound_answered_within_and_after_20_dict = outbound_answered_within_and_after_20(df)
        outbound_disconnected_within_and_after_20_dict = outbound_disconnected_within_and_after_20(df)

        # Calculate live agent metrics
        agent_live_dict = agent_live(agent_live_df)
        call_in_queue_dict = call_in_queue(agent_in_queue_df)

        # Calculate SLA and call status metrics
        SLA_dict = SLA(df)
        call_status_disposition_dict = call_status_disposition(df)

        # Calculate AHT-related metrics
        aht_agentwise_dict = aht_agentwise(df)
        aht_and_call_volume_dict = aht_and_call_volume(df)

        # Retrieve IVR performance data and calculate metrics
        df1 = IvrRepportSql(mydb, selected_campaign_name)
        ivr_performance_report_dict = ivr_performance_report(df1)

        # Return all calculated metrics as a tuple
        return [average_handling_time_dict, average_wait_time_dict, average_wrapup_time_dict,
                average_call_duration_dict, abandon_rate_dict, total_answered_call_dict,
                call_back_Scheduled_dict, agent_ideal_time_dict, average_queue_time_dict,
                inbound_abandon_within_and_after_20_dict, inbound_answered_within_and_after_20_dict,
                total_agent_manual_outbound_df, total_agent_progressive_inbound_df,
                total_agent_predictive_df, outbound_answered_within_and_after_20_dict,
                outbound_disconnected_within_and_after_20_dict, agent_live_dict, call_in_queue_dict,
                SLA_dict, call_status_disposition_dict, aht_agentwise_dict, aht_and_call_volume_dict,
                ivr_performance_report_dict]
    else:
        # Establish a connection to the SQL database
        mydb = sql_conn()

        # If the filter name is not "Today", just read CSV files
        df = read_csv_files(selected_campaign_name, start_date, end_date, today_date, selected_campaign_type, selected_agent_filter,selected_skills_name,selected_list_name)

        # Calculate metrics based on the data from CSV files
        average_handling_time_dict = average_handling_time(df)
        average_wait_time_dict = average_wait_time(df)
        average_wrapup_time_dict = average_wrapup_time(df)
        average_call_duration_dict = average_call_duration(df)
        abandon_rate_dict = abandon_rate(df)
        call_back_Scheduled_dict = call_back_Scheduled(df)
        total_answered_call_dict = total_answered_call(df)
        average_queue_time_dict = average_queue_time(df)
        inbound_abandon_within_and_after_20_dict = inbound_abandon_within_and_after_20(df)
        inbound_answered_within_and_after_20_dict = inbound_answered_within_and_after_20(df)
        inbound_answered_call_dict = inbound_answered_call(df)
        inbound_call_abandon_dict = inbound_call_abandon(df)
        outbound_answered_within_and_after_20_dict = outbound_answered_within_and_after_20(df)
        outbound_disconnected_within_and_after_20_dict = outbound_disconnected_within_and_after_20(df)
        outbound_answered_call_dict = outbound_answered_call(df)
        outbound_call_busy_dict = outbound_call_busy(df)
        outbound_call_disconnected_dict = outbound_call_disconnected(df)
        outbound_call_no_answered_dict = outbound_call_no_answered(df)
        SLA_dict = SLA(df)
        call_status_disposition_dict = call_status_disposition(df)
        aht_agentwise_dict = aht_agentwise(df)
        aht_and_call_volume_dict = aht_and_call_volume(df)


        # Return all calculated metrics as a tuple
        return [average_handling_time_dict, average_wait_time_dict, average_wrapup_time_dict,
                average_call_duration_dict, abandon_rate_dict, call_back_Scheduled_dict,
                total_answered_call_dict, average_queue_time_dict, inbound_abandon_within_and_after_20_dict,
                inbound_answered_within_and_after_20_dict, inbound_answered_call_dict, inbound_call_abandon_dict,
                outbound_answered_within_and_after_20_dict, outbound_disconnected_within_and_after_20_dict,
                outbound_answered_call_dict, outbound_call_busy_dict, outbound_call_disconnected_dict,
                outbound_call_no_answered_dict, SLA_dict, call_status_disposition_dict, aht_agentwise_dict,
                aht_and_call_volume_dict]
