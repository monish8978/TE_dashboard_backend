"""
    Import settings file
"""
from settings import common_csv_file_path, download_csv_row_data, compute_layer_log_path, start_count, end_count
# Import configuration settings related to file paths, logging, and date range from the 'settings' module

"""
    Import necessary modules
"""
from datetime import datetime, timedelta  # Modules for date and time operations
import pandas as pd  # Module for data manipulation and analysis
import traceback  # Module for printing stack traces to debug errors
import threading  # Module for multi-threading operations
import logging  # Module for logging messages
import os  # Module for interacting with the operating system
import re  # Module for regular expressions
import warnings  # Module to handle warnings

# Ignore warnings to prevent them from cluttering the output
warnings.filterwarnings("ignore")

# Configure logging to track the program's execution
logname = compute_layer_log_path
logging.basicConfig(filename=logname, level=logging.DEBUG)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
fh = logging.FileHandler(logname, mode='a+')
# Create a file handler to write log messages to the specified log file
formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)5s %(levelname)4s - %(lineno)3s - %(message)s")
fh.setFormatter(formatter)
log.addHandler(fh)
# Define the format of log messages and add the file handler to the logger

log.info("Loading....")
# Log an informational message indicating the start of the script execution

log = logging.getLogger('__main__')
# Get a logger specifically for the main module
lock = threading.Lock()
# Initialize a threading lock to ensure thread-safe operations

def csv_name():
    """
    Generates a list of CSV file names for the specified date range.

    Returns:
        list: A list of CSV file paths for each day within the date range.
    """
    try:
        file_name_list = []
        today = datetime.now()  # Get the current datetime
        for tmp_day_count in range(start_count, end_count):
            yesterday = today - timedelta(days=tmp_day_count)  # Calculate the date for each day in the range
            yesterday_date = yesterday.strftime('%Y-%m-%d')  # Format the date as 'YYYY-MM-DD'

            file_name = f"{common_csv_file_path}day_{yesterday_date}.csv"
            file_name_list.append(file_name)  # Add the file name to the list
        return file_name_list
    except Exception as err:
        log.error(str(err))  # Log any errors encountered during file name generation
        traceback.print_exc()  # Print the stack trace for debugging

def campaign_name_df(file_name_list):
    """
    Processes the CSV files to extract and save campaign names and their associated data.

    Args:
        file_name_list (list): A list of CSV file paths to process.

    Returns:
        None
    """
    try:
        for file_name in file_name_list:
            # Regular expression pattern to extract the date from the file name
            pattern = r'day_(\d{4}-\d{2}-\d{2})\.csv'

            # Search for the pattern in the file name
            match = re.search(pattern, file_name)

            if match:
                date_string = match.group(1)  # Extract the date string
            else:
                log.info("Date not found in the string.")  # Log if the date pattern is not found

            if os.path.exists(file_name):
                campaign_df = pd.read_csv(file_name)  # Read the CSV file into a DataFrame

                l = []
                campaign_name = set(campaign_df['campaign_name'])  # Extract unique campaign names
                for c in campaign_name:
                    data = c
                    l.append(data)
                df = pd.DataFrame(l)
                directory_path = f'{download_csv_row_data}/campaignname/'

                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)  # Create directory if it doesn't exist

                # Save the DataFrame to a CSV file with the campaign names
                a = df.to_csv(f'{download_csv_row_data}/campaignname/{date_string}.csv', index=False)

                for c in campaign_name:
                    df = campaign_df[campaign_df['campaign_name'] == c]  # Filter data for each campaign
                    overall_wise_call = df[["campaign_id", "campaign_name", "wrapup_time", "call_duration",
                                            "wait_time", "call_status_disposition", "next_call_time", "campaign_type",
                                            "agent_id", "q_enter_time", "q_leave_time", "call_start_date_time",
                                            "call_end_date_time"]]
                    directory_path = f'{download_csv_row_data}/{c}'
                    if not os.path.exists(directory_path):
                        os.makedirs(directory_path)  # Create directory if it doesn't exist
                    a = overall_wise_call.to_csv(f'{directory_path}/{date_string}.csv')  # Save the filtered data
    except Exception as err:
        log.error(str(err))  # Log any errors encountered during data processing
        traceback.print_exc()  # Print the stack trace for debugging

def delete_csv_file(file_name_list):
    """
    Deletes the specified CSV files from the file system.

    Args:
        file_name_list (list): A list of CSV file paths to delete.

    Returns:
        None
    """
    try:
        for file_name in file_name_list:
            if os.path.exists(file_name):
                os.remove(file_name)  # Delete the file
    except Exception as err:
        log.error(str(err))  # Log any errors encountered during file deletion
        traceback.print_exc()  # Print the stack trace for debugging

def main():
    """
    Main function to orchestrate the workflow:
    - Generate file names for the specified date range.
    - Process each CSV file to extract and save campaign data.
    - Delete the processed CSV files.

    Returns:
        None
    """
    file_name_list = csv_name()
    campaign_name_df(file_name_list)
    delete_csv_file(file_name_list)
