"""
    Import configuration settings and functions
"""
from settings import yearly_acquire_lock_log, yearly_file_path, yearly_acquire_lock_file
# Import configuration settings related to logging and file paths from the 'settings' module
from yearly_data_layer import main as main_dump_data
from yearly_compute_layer import main as main_compute_data
from yearly_data_layer_cmp import main as main_dump_data_cmp
from yearly_compute_layer_cmp import main as main_compute_data_cmp
# Import main functions from 'yearly_data_layer' and 'yearly_compute_layer' modules

"""
    Import necessary modules
"""
import traceback  # Module for printing stack traces to debug errors
import threading  # Module for multi-threading operations
import logging  # Module for logging messages
import psutil  # Module for process and system utilities
import fcntl  # Module for file control operations
import os  # Module for interacting with the operating system
import warnings  # Module to handle warnings

# Ignore warnings to prevent them from cluttering the output
warnings.filterwarnings("ignore")

# Configure logging to track the program's execution
logname = yearly_acquire_lock_log
logging.basicConfig(filename=logname, level=logging.DEBUG)
# Set up the logging configuration with DEBUG level
log = logging.getLogger()
log.setLevel(logging.DEBUG)
fh = logging.FileHandler(logname, mode='a+')
# Create a file handler to write log messages to the specified log file
formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)5s %(levelname)4s - %(lineno)3s - %(message)s")
fh.setFormatter(formatter)
log.addHandler(fh)
# Define the format of log messages and add the file handler to the logger

log.info("Loading ....")
# Log an informational message indicating the start of the script execution

log = logging.getLogger('__main__')
# Get a logger specifically for the main module
lock = threading.Lock()
# Initialize a threading lock to ensure thread-safe operations

def acquire_lock():
    """
    Acquires a lock by creating a lock file to prevent concurrent execution.

    Returns:
        bool: True if the lock is successfully acquired, False otherwise.
    """
    try:
        # Create the directory if it doesn't exist
        if not os.path.exists(yearly_file_path):
            os.makedirs(yearly_file_path)

        # Path and file name for the lock file
        tmp_file_path = f"{yearly_file_path}{yearly_acquire_lock_file}"
        with open(tmp_file_path, 'w') as lock_file:
            # Attempt to acquire an exclusive, non-blocking lock
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_file.write(str(os.getpid()))  # Write the process ID to the lock file
            lock_file.flush()
            fcntl.flock(lock_file, fcntl.LOCK_UN)  # Release the lock
        return True
    except IOError as err:
        log.error(str(err))  # Log any errors encountered during lock acquisition
        return False

def read_lock_file():
    """
    Reads the lock file to get the PID of the process that holds the lock.

    Returns:
        str: The PID from the lock file, or '0' if the file does not exist or is empty.
    """
    try:
        tmp_file_path = f"{yearly_file_path}{yearly_acquire_lock_file}"
        if os.path.exists(tmp_file_path):
            with open(tmp_file_path, 'r') as file:
                # Read lines from the file and strip leading/trailing whitespace
                file_contents_filter_data = [line.strip() for line in file.readlines()]

                # Return the last non-empty line, or '0' if the file is empty
                if file_contents_filter_data:
                    return file_contents_filter_data[-1] if file_contents_filter_data[-1] else '0'
                else:
                    return '0'
        else:
            return '0'
    except Exception as err:
        log.error(str(err))  # Log any errors encountered while reading the lock file
        traceback.print_exc()  # Print the stack trace for debugging

def is_already_running(pid):
    """
    Checks if a process with the given PID is currently running.

    Args:
        pid (str): The process ID to check.

    Returns:
        bool: True if the process is running, False otherwise.
    """
    try:
        pid = int(pid)  # Convert PID to an integer
        process = psutil.Process(pid)  # Create a process object for the given PID
        return process.is_running()  # Return whether the process is running
    except Exception as err:
        log.error(str(err))  # Log any errors encountered while checking process status
        return False

def main():
    """
    Main function to manage the execution workflow:
    - Check if another instance is running.
    - Acquire a lock to prevent concurrent execution.
    - Execute the data dumping and computing functions if not already running.
    """
    if os.path.exists(yearly_file_path):
        pid = read_lock_file()  # Read the PID from the lock file
    else:
        pid = '0'

    is_running = is_already_running(pid)  # Check if the process with the PID is running
    acquire_lock()  # Attempt to acquire the lock

    if not is_running:
        # If no other instance is running, proceed with data dumping and computing
        main_dump_data()
        main_compute_data()
        main_dump_data_cmp()
        main_compute_data_cmp()
    else:
        log.info("already running.....")  # Log if the process is already running

# Execute the main function if this script is run directly
if __name__ == "__main__":
    main()
