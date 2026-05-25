# Importing configuration file for various settings
from settings import acquire_lock_log, file_path, acquire_lock_file
from data_layer import main as main_dump_data
from data_layer_cmp import main as main_cmp_dump_data
from compute_layer import main as main_filter_data
from compute_layer_cmp import main as main_cmp_filter_data
from create_filter import main as main_create_filter
from compute_layer_function_agent import main as main_compute_layer_function_agent
from compute_layer_agent import main as main_filter_data_agent
from data_layer_agent import main as main_dump_data_agent


# Importing necessary modules
import traceback  # Module for printing stack traces to debug errors
import threading  # Module to handle multi-threading
import logging  # Module for logging messages
import psutil  # Module for process and system utilities
import fcntl  # Module for file locking (Unix only)
import os  # Module for interacting with the operating system
import warnings  # Module to handle warnings

# Ignore warnings to prevent them from cluttering the output
warnings.filterwarnings("ignore")

# Setting up logging to track the program's execution
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)s - %(message)s',  # Define the format of log messages
    level=logging.INFO,  # Set the logging level to INFO to capture informational messages
    filename=acquire_lock_log  # Specify the log file to write log messages to
)

# Initialize the main logger
log = logging.getLogger('__main__')  # Get a logger specifically for the main module

# Initialize a threading lock for thread synchronization
lock = threading.Lock()  # Create a lock object to ensure thread-safe operations

def acquire_lock():
    """
    Acquire an exclusive lock to ensure that only one instance of the script is running.
    """
    try:
        # Create the directory if it doesn't exist
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        # Path and file name for the lock file
        tmp_file_path = f"{file_path}{acquire_lock_file}"
        with open(tmp_file_path, 'w') as lock_file:
            # Acquire an exclusive lock on the lock file (non-blocking)
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Write the current process ID to the lock file
            lock_file.write(str(os.getpid()))
            lock_file.flush()  # Ensure data is written to the file
            # Release the lock (not necessary as file is closed, but good practice)
            fcntl.flock(lock_file, fcntl.LOCK_UN)
        return True  # Return True indicating lock acquisition was successful
    except IOError as err:
        log.error(str(err))  # Log any errors that occur during lock acquisition
        return False  # Return False indicating lock acquisition failed

def read_lock_file():
    """
    Read the process ID from the lock file to check if an instance is already running.
    """
    try:
        tmp_file_path = f"{file_path}{acquire_lock_file}"
        if os.path.exists(tmp_file_path):
            with open(tmp_file_path, 'r') as file:
                # Read lines from the lock file
                file_contents_filter_data = file.readlines()

                # Strip leading and trailing whitespaces from each line
                file_contents_filter_data = [line.strip() for line in file_contents_filter_data]

                # Check if the file is not empty
                if file_contents_filter_data:
                    file_contents_filter_data = file_contents_filter_data[-1]  # Get the last line (latest PID)
                    if len(file_contents_filter_data) != 0:
                        return file_contents_filter_data  # Return the PID
                    else:
                        return 0  # Return 0 if PID is empty
                else:
                    return 0  # Return 0 if file is empty
        else:
            return 0  # Return 0 if the lock file does not exist
    except Exception as err:
        log.error(str(err))  # Log any errors that occur during file reading
        traceback.print_exc()  # Print stack trace for debugging

def is_already_running(pid):
    """
    Check if a process with the given PID is already running.
    """
    try:
        pid = int(pid)  # Convert PID to integer
        process = psutil.Process(pid)  # Create a Process object for the given PID
        # Check if the process is running
        return process.is_running()
    except Exception as err:
        log.error(str(err))  # Log any errors that occur during process checking
        return False  # Return False indicating the process is not running or an error occurred

def main():
    """
    Main function to ensure only one instance of the script is running and execute the main tasks.
    """
    # Check if the lock file path exists
    if os.path.exists(file_path):
        pid = read_lock_file()  # Read the PID from the lock file
    else:
        pid = 0  # Set PID to 0 if the lock file path does not exist

    is_running = is_already_running(pid)  # Check if the process with the read PID is already running
    acquire_lock()  # Attempt to acquire the lock to ensure single instance execution

    # If the process is not already running, execute the main functions
    if not is_running:
        main_dump_data()  # Execute the main function for data dumping
        main_filter_data()  # Execute the main function for data filtering
        main_create_filter()  # Execute the main function for filter creation

        main_cmp_dump_data()
        main_cmp_filter_data()

        main_dump_data_agent()
        main_filter_data_agent()
        main_compute_layer_function_agent()
        main_filter_data_agent()
        main_dump_data_agent()
    else:
        log.info("Already running.....")  # Log message indicating the process is already running

# Check if the script is being run directly (not imported as a module)
if __name__ == "__main__":
    main()  # Execute the main function if the script is run directly

