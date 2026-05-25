"""
        import settings file
"""
from settings import common_csv_file_path, download_csv_row_data, compute_layer_log_path, day_count
# Import configuration settings from the 'settings' module

"""
        import modules
"""
from datetime import datetime, timedelta  # Modules for date and time operations
import pandas as pd  # Module for data manipulation and analysis
import traceback  # Module for printing stack traces to debug errors
import threading  # Module for multi-threading
import logging  # Module for logging messages
import os  # Module for interacting with the operating system
import warnings  # Module to handle warnings

# Ignore warnings to prevent them from cluttering the output
warnings.filterwarnings("ignore")

# Setting up logging to track the program's execution
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)s - %(message)s',  # Define the format of log messages
    level=logging.INFO,  # Set the logging level to INFO to capture informational messages
    filename=compute_layer_log_path  # Specify the log file to write log messages to
)

# Initialize the main logger
log = logging.getLogger('__main__')  # Get a logger specifically for the main module

# Initialize a threading lock for thread synchronization
lock = threading.Lock()  # Create a lock object to ensure thread-safe operations

def csv_name():
    """
    Generate the file name for the CSV file based on yesterday's date.
    """
    try:
        today = datetime.now()  # Get the current date and time
        yesterday = today - timedelta(days=day_count)  # Calculate the date for yesterday
        yesterday_date = yesterday.strftime('%Y-%m-%d')  # Format the date as a string

        # Construct the file name using the common file path and yesterday's date
        file_name = f"{common_csv_file_path}day_{yesterday_date}.csv"
        return file_name, yesterday_date  # Return the file name and formatted date
    except Exception as err:
        log.error(str(err))  # Log any errors that occur during file name generation
        traceback.print_exc()  # Print stack trace for debugging

def read_file(file_name):
    """
    Read the CSV file and return its contents as a DataFrame.
    """
    try:
        if os.path.exists(file_name):  # Check if the file exists
            df = pd.read_csv(file_name)  # Read the CSV file into a DataFrame
            return df  # Return the DataFrame
    except Exception as err:
        log.error(str(err))  # Log any errors that occur during file reading
        traceback.print_exc()  # Print stack trace for debugging

def campaign_name_df(yesterday_date, campaign_df):
    """
    Extract unique campaign names from the DataFrame and save them to a CSV file.
    """
    try:
        l = []  # List to hold unique campaign names
        if campaign_df is not None:  # Check if the DataFrame is not empty
            campaign_name = set(campaign_df['campaign_name'])  # Extract unique campaign names
            for c in campaign_name:
                l.append(c)  # Append each campaign name to the list
            df = pd.DataFrame(l)  # Create a DataFrame from the list
            directory_path = f'{download_csv_row_data}/campaignname/'  # Directory to save the file

            if not os.path.exists(directory_path):  # Check if the directory exists
                os.makedirs(directory_path)  # Create the directory if it doesn't exist

            # Save the campaign names DataFrame to a CSV file
            df.to_csv(f'{download_csv_row_data}/campaignname/{yesterday_date}.csv', index=False)
            return campaign_name  # Return the set of campaign names
    except Exception as err:
        log.error(str(err))  # Log any errors that occur during campaign name extraction
        traceback.print_exc()  # Print stack trace for debugging

def create_csv_filter(yesterday_date, campaign_name, campaign_df):
    """
    Create separate CSV files for each campaign and save their details.
    """
    try:
        if campaign_df is not None:  # Check if the DataFrame is not empty
            for c in campaign_name:  # Iterate over each campaign name
                df = campaign_df[campaign_df['campaign_name'] == c]  # Filter DataFrame for the current campaign
                overall_wise_call = df[["agent_id","agent_name","campaign_id", "campaign_name", "wrapup_time", "call_duration", "wait_time",
                                        "call_status_disposition", "next_call_time", "campaign_type", "agent_id",
                                        "q_enter_time", "q_leave_time", "call_start_date_time", "call_end_date_time", "skills", "list_name"]]  # Select relevant columns
                directory_path = f'{download_csv_row_data}/{c}'  # Directory to save the file for the current campaign
                if not os.path.exists(directory_path):  # Check if the directory exists
                    os.makedirs(directory_path)  # Create the directory if it doesn't exist
                # Save the campaign-specific DataFrame to a CSV file
                overall_wise_call.to_csv(f'{directory_path}/{yesterday_date}.csv')
    except Exception as err:
        log.error(str(err))  # Log any errors that occur during CSV file creation
        traceback.print_exc()  # Print stack trace for debugging

def main():
    """
    Main function to execute the CSV generation and processing.
    """
    file_name, yesterday_date = csv_name()  # Generate the CSV file name and date
    campaign_df = read_file(file_name)  # Read the CSV file into a DataFrame
    campaign_name = campaign_name_df(yesterday_date, campaign_df)  # Extract and save unique campaign names
    create_csv_filter(yesterday_date, campaign_name, campaign_df)  # Create and save filtered CSV files for each campaign

# Execute the main function if the script is run directly
if __name__ == "__main__":
    main()