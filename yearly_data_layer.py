"""
    Import settings file
"""
from settings import mysql_info, common_csv_file_path, data_layer_log_path, start_count, end_count
# Import configuration settings related to MySQL connection, file paths, and date range from the 'settings' module

"""
    Import necessary modules
"""
from datetime import datetime, timedelta  # Modules for date and time operations
import pandas as pd  # Module for data manipulation and analysis
import traceback  # Module for printing stack traces to debug errors
import threading  # Module for multi-threading operations
import logging  # Module for logging messages
import pymysql  # Module for connecting to a MySQL database
import os  # Module for interacting with the operating system
import warnings  # Module to handle warnings

# Ignore warnings to prevent them from cluttering the output
warnings.filterwarnings("ignore")

# Configure logging to track the program's execution
logname = data_layer_log_path
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

def sql_conn():
    """
    Handles SQL connection to a MySQL database.

    Args:
        None: Uses configuration variables from the config file.

    Returns:
        db (pymysql.connections.Connection): Returns a database connection object after creating the connection.
    """
    db = ""
    try:
        # Create a connection to the MySQL database using credentials from the settings file
        db = pymysql.connect(
            host=mysql_info['host'],
            user=mysql_info['user'],
            password=mysql_info['password'],
            db=mysql_info['database']
        )
    except Exception as err:
        # Log any error that occurs during the connection attempt
        log.error("Not Able to connect mysql reason is " + str(err))
        traceback.print_exc()  # Print the stack trace for debugging
    return db  # Return the database connection object

def date_time():
    """
    Generates a list of dates within the specified date range.

    Returns:
        list: A list of datetime.date objects for each day within the date range.
    """
    today = datetime.now()  # Get the current datetime
    date_list = []
    for tmp_day_count in range(start_count, end_count):
        yesterday_date = today.date() - timedelta(days=tmp_day_count)  # Calculate the date for each day in the range
        date_list.append(yesterday_date)  # Add the date to the list
    return date_list  # Return the list of dates

def dump_data(mydb, date_list):
    """
    Dumps data from the MySQL database into CSV files for each date in the list.

    Args:
        mydb (pymysql.connections.Connection): The database connection object.
        date_list (list): A list of datetime.date objects to query the database.

    Returns:
        None
    """
    # Create directory if it doesn't exist
    if not os.path.exists(common_csv_file_path):
        os.makedirs(common_csv_file_path)

    try:
        for yesterday_date in date_list:
            yesterday_date = str(yesterday_date)  # Convert date to string
            date_obj = datetime.strptime(yesterday_date, "%Y-%m-%d")  # Convert string to datetime object

            # Extract year and month
            year_month = date_obj.strftime("%Y_%m")
            # Define the file name and SQL query
            filename = f"day_{yesterday_date}.csv"
            query = f"""
            SELECT agent_id, agent_name, campaign_id, campaign_name, wrapup_time, call_duration,
                   wait_time, call_status_disposition, next_call_time, campaign_type, agent_id,
                   q_enter_time, q_leave_time, call_start_date_time, call_end_date_time
            FROM {year_month}
            WHERE DATE(call_start_date_time) = '{yesterday_date}'
            """

            try:
                # Execute the SQL query and read the results into a DataFrame
                df = pd.read_sql(query, con=mydb)

                # Save the DataFrame to a CSV file if it's not empty
                if not df.empty:
                    df.to_csv(f"{common_csv_file_path}{filename}", index=False)
            except Exception as query_err:
                # Log any errors that occur during the SQL query execution
                log.error("Error executing SQL query: " + str(query_err))
                traceback.print_exc()  # Print the stack trace for debugging
    except Exception as err:
        # Log any errors that occur during the file operations
        log.error(str(err))
        traceback.print_exc()  # Print the stack trace for debugging

def main():
    """
    Main function that orchestrates the workflow of connecting to the database,
    generating the date list, and dumping data into CSV files.

    Returns:
        None
    """
    mydb = sql_conn()  # Establish a connection to the database
    date_list = date_time()  # Generate a list of dates
    dump_data(mydb, date_list)  # Dump the data into CSV files

# Execute the main function if this script is run directly
if __name__ == "__main__":
    main()
