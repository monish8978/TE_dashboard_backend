"""
        import settings file
"""
from settings import common_csv_file_path, download_csv_row_data, create_filter_log_path, day_count, filter_path
# Import configuration settings from the 'settings' module.
# - `common_csv_file_path`: Base path for common CSV files.
# - `download_csv_row_data`: Directory path for saving CSV files with row data.
# - `compute_layer_log_path`: Path for the log file in the compute layer.
# - `day_count`: Number of days to subtract for generating the date.
# - `filter_path`: Path for filter-related files.

"""
        import modules
"""
from compute_layer_functions import main_test
# Import the main_test function from the `compute_layer_functions` module.
# This function will be used to perform computations on the data.

from datetime import datetime, timedelta  # Modules for date and time operations
import pandas as pd  # Module for data manipulation and analysis
import traceback  # Module for printing stack traces to debug errors
import threading  # Module for multi-threading
import logging  # Module for logging messages
import shutil  # Module for high-level file operations
import json  # Module for working with JSON data
import os  # Module for interacting with the operating system
import warnings  # Module to handle warnings

# Ignore warnings to prevent them from cluttering the output
warnings.filterwarnings("ignore")

# Setting up logging to track the program's execution
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)s - %(message)s',  # Define the format of log messages
    level=logging.INFO,  # Set the logging level to INFO to capture informational messages
    filename=create_filter_log_path  # Specify the log file to write log messages to
)

# Initialize the main logger
log = logging.getLogger('__main__')  # Get a logger specifically for the main module

# Initialize a threading lock for thread synchronization
lock = threading.Lock()  # Create a lock object to ensure thread-safe operations


def csv_name():
      try:
            # Get the current date and time
            today = datetime.now()
            # Calculate the date for 'yesterday' by subtracting `day_count` days from the current date
            yesterday = today - timedelta(days=day_count)
            # Format the 'yesterday' date as a string in the format 'YYYY-MM-DD'
            yesterday_date = yesterday.strftime('%Y-%m-%d')

            # Construct the file name for the CSV file based on the formatted 'yesterday' date
            file_name = f"{common_csv_file_path}day_{yesterday_date}.csv"
            # Return the file name and the formatted 'yesterday' date
            return file_name, yesterday_date
      except Exception as err:
            # Log any exception that occurs during the execution of the try block
            log.error(str(err))
            # Print the stack trace for debugging purposes
            traceback.print_exc()

def read_file(file_name):
    """
    Reads a CSV file into a pandas DataFrame.

    Args:
    - file_name (str): The path to the CSV file to be read.

    Returns:
    - pd.DataFrame: A DataFrame containing the data from the CSV file if it exists; otherwise, returns None.

    Raises:
    - Exception: Logs an error and prints the stack trace if reading the file fails.
    """
    try:
        # Check if the file exists at the specified path
        if os.path.exists(file_name):
            # Attempt to read the CSV file into a DataFrame using pandas
            df = pd.read_csv(file_name)
            # Return the DataFrame containing the data from the CSV file
            return df
    except Exception as err:
        # If an exception occurs, log the error message
        log.error(str(err))
        # Print the stack trace of the exception for debugging
        traceback.print_exc()


def campaign_name_df(yesterday_date, campaign_df):
    """
    Extracts unique campaign names from a DataFrame and saves them to a CSV file.

    Args:
    - yesterday_date (str): The date string to be used in the CSV file name (format: 'YYYY-MM-DD').
    - campaign_df (pd.DataFrame): DataFrame containing a column 'campaign_name' with campaign names.

    Returns:
    - set: A set of unique campaign names extracted from the DataFrame.

    Raises:
    - Exception: Logs an error and prints the stack trace if any issues occur during the process.
    """
    try:
        l = []
        # Check if the DataFrame is not None
        if campaign_df is not None:
            # Extract unique campaign names from the DataFrame
            campaign_name = set(campaign_df['campaign_name'])
            # Append each campaign name to the list
            for c in campaign_name:
                data = c
                l.append(data)
            # Create a new DataFrame from the list of unique campaign names
            df = pd.DataFrame(l, columns=['campaign_name'])
            # Define the directory path for saving the CSV file
            directory_path = f'{download_csv_row_data}/campaignname/'

            # Create the directory if it does not exist
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            # Save the DataFrame to a CSV file with the date as part of the file name
            df.to_csv(f'{directory_path}/{yesterday_date}.csv', index=False)
            # Return the set of unique campaign names
            return campaign_name
    except Exception as err:
        # If an exception occurs, log the error message
        log.error(str(err))
        # Print the stack trace of the exception for debugging
        traceback.print_exc()

def get_agent_list(campaign_df, campaign):
    try:
        df = campaign_df[campaign_df["campaign_name"] == campaign]
        agent_list = df["agent_id"].dropna().unique().tolist()

        if agent_list:  # list empty nahi hai
            agent_list.insert(0, "ALL")

        return agent_list

    except Exception as e:
        log.error(str(e))
        return []


def campaign_type_filter():
    """
    Returns a list of campaign types available for filtering.

    Returns:
    - list: A list of campaign types including "ALL", "INBOUND", and "OUTBOUND".

    Raises:
    - Exception: Logs an error and prints the stack trace if any issues occur during the process.
    """
    try:
        # Define a list of campaign types
        campaign_type_list = ["ALL", "INBOUND", "OUTBOUND"]
        # Return the list of campaign types
        return campaign_type_list
    except Exception as err:
        # If an exception occurs, log the error message
        log.error(str(err))
        # Print the stack trace of the exception for debugging
        traceback.print_exc()



def get_date_range():
    """
    Generates various date ranges for filtering data and returns them in a dictionary.

    Returns:
    - tuple: A tuple containing:
        - dict: A dictionary with keys representing different date ranges and their corresponding start and end dates.
        - datetime: The current date and time.

    Raises:
    - Exception: Logs an error and prints the stack trace if any issues occur during the process.
    """
    try:
        from datetime import datetime, timedelta

        # Get the current date and time
        today = datetime.now() - timedelta(days=0)  # Today

        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)  # Yesterday

        # Calculate the start date 7 days ago from yesterday
        seven_day_date = yesterday - timedelta(days=7)  # 7 Days ago

        # Calculate the start date 30 days ago from yesterday
        thirty_day_date = yesterday - timedelta(days=30)  # 30 Days ago

        # Calculate the start date 3 months ago from yesterday
        three_months_date = yesterday - timedelta(days=3*30)  # Approx. 3 Months ago

        # Calculate the start date 6 months ago from yesterday
        six_months_date = yesterday - timedelta(days=6*30)  # Approx. 6 Months ago

        # Calculate the start date 1 year ago from yesterday
        year_date = yesterday - timedelta(days=365)  # 1 Year ago

        # Define the date ranges as lists of strings in 'YYYY-MM-DD' format
        today_list = [today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')]
        yesterday_list = [yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')]
        seven_day_list = [seven_day_date.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')]
        thirty_day_list = [thirty_day_date.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')]
        three_months_list = [three_months_date.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')]
        six_months_list = [six_months_date.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')]
        year_date_list = [year_date.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')]
        Customize_Date_list = [year_date.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')]

        # Create a dictionary to map date range descriptions to their corresponding date lists
        date_range_dict = {
            "Today": today_list,
            "Yesterday": yesterday_list,
            "Last 7 Days": seven_day_list,
            "Last Thirty Days": thirty_day_list,
            "Last 3 Months": three_months_list,
            "Last 6 Months": six_months_list,
            "Last Year": year_date_list,
            "Customize Date": Customize_Date_list
        }

        return date_range_dict, today

    except Exception as err:
        # Log any errors that occur and print the stack trace for debugging
        log.error(str(err))
        traceback.print_exc()

class NumpyEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for handling numpy data types.

    This class extends the default JSONEncoder to correctly serialize numpy data types
    to JSON-serializable formats. It is useful for ensuring that numpy-specific objects
    can be converted to JSON without errors.

    Methods:
    - default(obj): Converts numpy data types to standard Python types for JSON serialization.
    """

    def default(self, obj):
        """
        Override the default method of JSONEncoder to handle numpy data types.

        Args:
        - obj (any): The object to be encoded into JSON format.

        Returns:
        - any: A JSON-serializable version of the input object.

        If the object is a numpy integer, floating-point number, or ndarray, it is converted
        to its corresponding standard Python type. If the object is not a numpy type, the
        method calls the default encoder's `default` method.

        Raises:
        - TypeError: If the object cannot be serialized and does not match any handled type.
        """
        import numpy as np  # Import numpy inside the method to avoid unnecessary imports if not used

        if isinstance(obj, np.integer):
            # Convert numpy integer to a standard Python int
            return int(obj)
        elif isinstance(obj, np.floating):
            # Convert numpy float to a standard Python float
            return float(obj)
        elif isinstance(obj, np.ndarray):
            # Convert numpy array to a standard Python list
            return obj.tolist()

        # For objects that are not numpy types, use the default method of JSONEncoder
        return json.JSONEncoder.default(self, obj)

def create_json_filter(campaign_name,campaign_df,date_range_dict,today):
      try:
            today = today.strftime('%Y-%m-%d')

            yesterday_filter = date_range_dict['Yesterday']
            Last_7_Days_filter = date_range_dict['Last 7 Days']
            Last_Thirty_Days_filter = date_range_dict['Last Thirty Days']
            Last_3_Months_filter = date_range_dict['Last 3 Months']
            Last_6_Months_filter = date_range_dict['Last 6 Months']
            Last_Year_filter = date_range_dict['Last Year']
            Customize_Date_filter = date_range_dict['Customize Date']

            tmp_selected_campaign_type_list = ["ALL","INBOUND","OUTBOUND"]
            selected_filter_name_list = ["Yesterday","Last 7 Days","Last Thirty Days","Last 3 Months","Last 6 Months","Last Year","Customize Date"]

            selected_filter_name_y = selected_filter_name_list[0]
            selected_filter_name_7 = selected_filter_name_list[1]
            selected_filter_name_t = selected_filter_name_list[2]
            selected_filter_name_3 = selected_filter_name_list[3]
            selected_filter_name_6 = selected_filter_name_list[4]
            selected_filter_name_yr = selected_filter_name_list[5]
            selected_filter_name_cd = selected_filter_name_list[6]

            selected_campaign_type_a = tmp_selected_campaign_type_list[0]
            selected_campaign_type_i = tmp_selected_campaign_type_list[1]
            selected_campaign_type_o = tmp_selected_campaign_type_list[2]

            # Ensure all parts of the path are strings
            # filter_path = str(filter_path)


            if campaign_name != None:

                for selected_campaign_name in campaign_name:
                    selected_campaign_name = str(selected_campaign_name)

                    selected_filter_name_y = str(selected_filter_name_y)
                    selected_filter_name_7 = str(selected_filter_name_7)
                    selected_filter_name_t = str(selected_filter_name_t)
                    selected_filter_name_3 = str(selected_filter_name_3)
                    selected_filter_name_6 = str(selected_filter_name_6)
                    selected_filter_name_cd = str(selected_filter_name_cd)

                    selected_filter_name_yr = str(selected_filter_name_yr)
                    selected_campaign_type_a = str(selected_campaign_type_a)
                    selected_campaign_type_i = str(selected_campaign_type_i)
                    selected_campaign_type_o = str(selected_campaign_type_o)

                    agent_list = get_agent_list(campaign_df, selected_campaign_name)
                    selected_skills_name = "ALL"
                    selected_list_name = "ALL"

                    today = str(today)
                    for agent_id in agent_list:
                        selected_agent_filter_a = str(agent_id)
                        if selected_filter_name_y == "Yesterday":
                            start_date = yesterday_filter[0]
                            end_date = yesterday_filter[1]
                            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                            if selected_campaign_type_a == "ALL":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_y,selected_campaign_type_a,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_y, selected_campaign_type_a, f"{today}.json")


                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_i == "INBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_y,selected_campaign_type_i,selected_agent_filter_a,selected_skills_name,selected_list_name)


                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_y, selected_campaign_type_i, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_o == "OUTBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_y,selected_campaign_type_o,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_y, selected_campaign_type_o, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                        if selected_filter_name_7 == "Last 7 Days":
                            start_date = Last_7_Days_filter[0]
                            end_date = Last_7_Days_filter[1]
                            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                            if selected_campaign_type_a == "ALL":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_7,selected_campaign_type_a,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_7, selected_campaign_type_a, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_i == "INBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_7,selected_campaign_type_i,selected_agent_filter_a,selected_skills_name,selected_list_name)


                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_7, selected_campaign_type_i, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_o == "OUTBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_7,selected_campaign_type_o,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_7, selected_campaign_type_o, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                        if selected_filter_name_t == "Last Thirty Days":
                            start_date = Last_Thirty_Days_filter[0]
                            end_date = Last_Thirty_Days_filter[1]
                            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                            if selected_campaign_type_a == "ALL":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_t,selected_campaign_type_a,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_t, selected_campaign_type_a, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_i == "INBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_t,selected_campaign_type_i,selected_agent_filter_a,selected_skills_name,selected_list_name)


                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_t, selected_campaign_type_i, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)


                            if selected_campaign_type_o == "OUTBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_t,selected_campaign_type_o,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_t, selected_campaign_type_o, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                        if selected_filter_name_3 == "Last 3 Months":
                            start_date = Last_3_Months_filter[0]
                            end_date = Last_3_Months_filter[1]
                            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                            if selected_campaign_type_a == "ALL":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_3,selected_campaign_type_a,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_3, selected_campaign_type_a, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_i == "INBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_3,selected_campaign_type_i,selected_agent_filter_a,selected_skills_name,selected_list_name)


                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_3, selected_campaign_type_i, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_o == "OUTBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_3,selected_campaign_type_o,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_3, selected_campaign_type_o, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                        if selected_filter_name_6 == "Last 6 Months":
                            start_date = Last_6_Months_filter[0]
                            end_date = Last_6_Months_filter[1]
                            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                            if selected_campaign_type_a == "ALL":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_6,selected_campaign_type_a,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_6, selected_campaign_type_a, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_i == "INBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_6,selected_campaign_type_i,selected_agent_filter_a,selected_skills_name,selected_list_name)


                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_6, selected_campaign_type_i, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_o == "OUTBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_6,selected_campaign_type_o,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_6, selected_campaign_type_o, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                        if selected_filter_name_yr == "Last Year":
                            start_date = Last_Year_filter[0]
                            end_date = Last_Year_filter[1]
                            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                            if selected_campaign_type_a == "ALL":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_yr,selected_campaign_type_a,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_yr, selected_campaign_type_a, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_i == "INBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_yr,selected_campaign_type_i,selected_agent_filter_a,selected_skills_name,selected_list_name)


                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)


                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_yr, selected_campaign_type_i, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_o == "OUTBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_yr,selected_campaign_type_o,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_yr, selected_campaign_type_o, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                        if selected_filter_name_cd == "Customize Date":
                            start_date = Last_Year_filter[0]
                            end_date = Last_Year_filter[1]
                            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                            if selected_campaign_type_a == "ALL":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_cd,selected_campaign_type_a,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                # date range
                                date_range_dir = str(start_date)+"_"+str(end_date)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_cd, selected_campaign_type_a,date_range_dir, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_i == "INBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_cd,selected_campaign_type_i,selected_agent_filter_a,selected_skills_name,selected_list_name)


                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                # date range
                                date_range_dir = str(start_date)+"_"+str(end_date)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_cd, selected_campaign_type_i,date_range_dir, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

                            if selected_campaign_type_o == "OUTBOUND":
                                average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict = main_test(selected_campaign_name,start_date,end_date,selected_filter_name_cd,selected_campaign_type_o,selected_agent_filter_a,selected_skills_name,selected_list_name)

                                tmp_list = [average_handling_time_dict,average_wait_time_dict,average_wrapup_time_dict,average_call_duration_dict,abandon_rate_dict,call_back_Scheduled_dict,total_answered_call_dict,average_queue_time_dict,inbound_abandon_within_and_after_20_dict,inbound_answered_within_and_after_20_dict,inbound_answered_call_dict,inbound_call_abandon_dict,outbound_answered_within_and_after_20_dict,outbound_disconnected_within_and_after_20_dict,outbound_answered_call_dict,outbound_call_busy_dict,outbound_call_disconnected_dict,outbound_call_no_answered_dict,SLA_dict,call_status_disposition_dict,aht_agentwise_dict,aht_and_call_volume_dict]

                                # Convert dictionary to JSON with custom encoder
                                json_data = json.dumps(tmp_list, cls=NumpyEncoder, indent=4)

                                # date range
                                date_range_dir = str(start_date)+"_"+str(end_date)

                                tmp_file_path = os.path.join(filter_path, selected_campaign_name,selected_agent_filter_a, selected_filter_name_cd, selected_campaign_type_o,date_range_dir, f"{today}.json")

                                if not os.path.exists(tmp_file_path):
                                    # Create directory if it doesn't exist
                                    os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)

                                    # Write the JSON data to a file
                                    with open(tmp_file_path, 'w') as json_file:
                                        json_file.write(json_data)

      except Exception as err:
            log.error(str(err))
            traceback.print_exc()


def remove_filter():
    """
    Deletes the directory specified by `filter_path` and logs the outcome.

    This function attempts to delete the entire directory at `filter_path`.
    It handles potential errors that might occur during the deletion process,
    such as permission issues or the directory not existing. The function logs
    detailed error messages if any exceptions are encountered.

    Returns:
    - None
    """
    try:
        # Try to handle directory deletion
        try:
            # Attempt to delete the directory and its contents
            shutil.rmtree(filter_path)
            # Log success message indicating that the directory has been deleted
            log.info(f"Deleted directory: {filter_path}")
        except Exception as e:
            # Log an error message if there was an issue deleting the directory
            # This could include issues like permission errors or the directory not being found
            log.error(f"Error deleting directory {filter_path}: {e}")

    except Exception as err:
        # Print the stack trace for debugging purposes, providing detailed
        # information about the exception that occurred
        traceback.print_exc()
        # Log the error message to keep a record of the issue
        log.error(str(err))

def delete_csv_file(yesterday_date):
    """
    Deletes a CSV file for the given date.

    This function constructs the file path for a CSV file based on the provided
    date and attempts to delete it if it exists. It logs any errors encountered
    during the deletion process.

    Args:
    - yesterday_date (str): The date used to construct the file name, formatted as 'YYYY-MM-DD'.

    Returns:
    - None
    """
    try:
        # Construct the file name using the provided date
        file_name = f"{common_csv_file_path}day_{yesterday_date}.csv"
        # Build the full file path
        file_path = os.path.join(file_name)

        # Check if the file exists before attempting to delete it
        if os.path.exists(file_path):
            # Remove the file from the filesystem
            os.remove(file_path)
            log.info(f"Deleted file: {file_path}")
        else:
            # Log a message if the file does not exist
            log.info(f"File does not exist: {file_path}")
    except Exception as err:
        # Log the error message if an exception occurs during file deletion
        log.error(f"Error deleting file {file_path}: {err}")
        # Print the stack trace to provide detailed debugging information
        traceback.print_exc()


def main():
    """
    Main function that orchestrates the workflow of removing old filters,
    processing campaign data, generating date ranges, creating JSON filters,
    and deleting old CSV files.

    This function performs the following operations in sequence:
    1. Removes old filter files.
    2. Retrieves the CSV file path and the date for the previous day.
    3. Reads the campaign data from the CSV file.
    4. Extracts unique campaign names from the data.
    5. Obtains date ranges for various periods.
    6. Creates JSON filters based on campaign names, campaign data, and date ranges.
    7. Deletes the CSV file for the previous day.

    Returns:
    - None
    """

    # Step 1: Remove old filter files
    remove_filter()

    # Step 2: Retrieve the file name and date for the previous day
    file_name, yesterday_date = csv_name()

    # Step 3: Read the CSV file into a DataFrame
    campaign_df = read_file(file_name)

    # Step 4: Extract unique campaign names from the DataFrame
    campaign_name = campaign_name_df(yesterday_date, campaign_df)

    # Step 5: Obtain date ranges for various periods
    date_range_dict, today = get_date_range()

    # Step 6: Create JSON filters using campaign names, campaign data, and date ranges
    create_json_filter(campaign_name, campaign_df, date_range_dict, today)

    # Step 7: Delete the CSV file for the previous day
    delete_csv_file(yesterday_date)



if __name__ == "__main__":
    main()