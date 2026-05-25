"""
    Import settings file
"""
from settings import mysql_info, common_csv_file_path, data_layer_log_path, day_count
# Import configuration settings from the 'settings' module

"""
    Import modules
"""
from datetime import datetime, timedelta  # Modules for date and time operations
import pandas as pd  # Module for data manipulation and analysis
import traceback  # Module for printing stack traces to debug errors
import threading  # Module for multi-threading
import logging  # Module for logging messages
import pymysql  # Module for connecting to a MySQL database
import os  # Module for interacting with the operating system
import warnings  # Module to handle warnings

# Ignore warnings to prevent them from cluttering the output
warnings.filterwarnings("ignore")

# Setting up logging to track the program's execution
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)s - %(message)s',  # Define the format of log messages
    level=logging.INFO,  # Set the logging level to INFO to capture informational messages
    filename=data_layer_log_path  # Specify the log file to write log messages to
)

# Initialize the main logger
log = logging.getLogger('__main__')  # Get a logger specifically for the main module

# Initialize a threading lock for thread synchronization
lock = threading.Lock()  # Create a lock object to ensure thread-safe operations


def sql_conn():
    """
    Handles SQL connection to a MySQL database.

    Args:
        None: Uses configuration variables from the config file.

    Returns:
        db (pymysql.connections.Connection): Returns a database connection object after creating the connection.
    """
    db = ""  # Initialize database connection variable
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
    Calculates the date for the previous day and the corresponding year-month format.

    Returns:
        yesterday_date (datetime.date): The date for the previous day.
        year_month (str): The year and month formatted as "YYYY_MM".
    """
    today = datetime.now()  # Get the current datetime
    yesterday_date = today.date() - timedelta(days=day_count)  # Calculate the date for the previous day
    year_month = yesterday_date.strftime("%Y_%m")  # Format the date into "YYYY_MM"
    return yesterday_date, year_month  # Return the previous day's date and year-month

def dump_data(mydb, yesterday_date, year_month):
    """
    Dumps data from the MySQL database into a CSV file.

    Args:
        mydb (pymysql.connections.Connection): The database connection object.
        yesterday_date (datetime.date): The date for the previous day.
        year_month (str): The year and month formatted as "YYYY_MM".

    Returns:
        None
    """
    # Create directory if it doesn't exist
    if not os.path.exists(common_csv_file_path):
        os.makedirs(common_csv_file_path)

    try:
        # Define the file name and SQL query
        filename = f"day_{yesterday_date}.csv"
        query = f"""
        SELECT agent_id, agent_name, campaign_id, campaign_name, wrapup_time, call_duration,
               wait_time, call_status_disposition, next_call_time, campaign_type, agent_id,
               q_enter_time, q_leave_time, call_start_date_time, call_end_date_time, skills, list_name
        FROM {year_month}
        WHERE DATE(call_start_date_time) = '{yesterday_date}'
        """

        # Execute the SQL query and read the results into a DataFrame
        df = pd.read_sql(query, con=mydb)
        # print(df)  # Print DataFrame for debugging purposes

        # Save the DataFrame to a CSV file if it's not empty
        if not df.empty:
            df.to_csv(f"{common_csv_file_path}{filename}", index=False)
    except Exception as err:
        # Log any errors that occur during data dumping
        log.error(str(err))
        traceback.print_exc()  # Print the stack trace for debugging

def main():
    """
    Main function that orchestrates the workflow of connecting to the database,
    calculating the previous day's date, and dumping data into a CSV file.

    Returns:
        None
    """
    mydb = sql_conn()  # Establish a connection to the database
    yesterday_date, year_month = date_time()  # Get the previous day's date and year-month
    dump_data(mydb, yesterday_date, year_month)  # Dump the data into a CSV file

# Execute the main function if the script is run directly
if __name__ == "__main__":
    main()
