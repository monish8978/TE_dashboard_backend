# ------------------ MySQL Database Configuration ------------------

mysql_info = {
    "host": "localhost",                           # IP address or hostname of the MySQL server
    "user": "root",                                # Username to connect to the MySQL server
    "password": "sqladmin",                        # Password associated with the MySQL user
    "database": "czentrix_campaign_manager"        # Name of the database being accessed
}

# ------------------ API Server Configuration ------------------

api_ip = "172.16.1.247"    # IP address of the REST API server (used for inter-service communication)
api_port = 50002           # Port on which the API server is listening

# ------------------ Operation Control Variables ------------------


live_day_count = 0
day_count = 1      # Represents the number of days used in certain time-based operations (e.g., data fetch for the last N days)

start_count = 1     # Starting index or ID for a looped operation (e.g., filtering or processing records)
end_count = 50      # Ending index or ID for a looped operation

# Define the threshold time in seconds
Threshold = 20

# ------------------ Log File Paths ------------------

# These logs help track each layer or module of the system

data_layer_log_path = '/var/log/czentrix/TE_dashboard/data_layer.log'
# Logs for data extraction and transformation layer

compute_layer_log_path = '/var/log/czentrix/TE_dashboard/compute_layer.log'
# Logs for core compute operations (e.g., analytics, metrics calculation)

compute_layer_function_log_path = '/var/log/czentrix/TE_dashboard/compute_layer_function.log'
# Logs specifically for function-level details within compute operations

compute_layer_function_api_log_path = '/var/log/czentrix/TE_dashboard/compute_layer_function_api.log'
# Logs for API calls made from within compute layer functions

create_filter_log_path = "/var/log/czentrix/TE_dashboard/create_filter.log"
# Logs related to dynamic filter creation by users or the system

live_data_log_path = '/var/log/czentrix/TE_dashboard/live_data.log'
# Tracks real-time or near real-time data processing

acquire_lock_log = '/var/log/czentrix/TE_dashboard/acquire_lock.log'
# Logs for file or process locking operations to prevent conflicts

yearly_acquire_lock_log = '/var/log/czentrix/TE_dashboard/yearly_acquire_lock.log'
# Logs specifically for annual processes that use locking

log_path_check_service_backend = '/var/log/czentrix/TE_dashboard/service_check_backend.log'
# Logs for health checks or status monitoring of backend services

delete_old_csv_files = '/var/log/czentrix/TE_dashboard/delete_old_csv_files.log'
# Logs specific to file cleanup operations for old CSV files

# ------------------ CSV Storage Paths ------------------

common_csv_file_path = '/var/log/czentrix/TE_dashboard/data_layer_csv_output/'
# Directory where general CSV output files from the data layer are saved

common_csv_cmp_file_path = '/var/log/czentrix/TE_dashboard/data_layer_cmp_csv_output/'
# Directory where comparison or campaign-related CSV files are saved

common_csv_file_path_agent = '/var/log/czentrix/TE_dashboard/agent_state_analysis/data_layer_csv_output/'
# Directory where comparison or agent-related CSV files are saved


download_csv_row_data = '/var/log/czentrix/TE_dashboard/download_csv_row_data/hitorical_data/'
# Directory for downloaded historical data in CSV format

download_csv_row_data_agent = '/var/log/czentrix/TE_dashboard/agent_state_analysis/hitorical_data/'
# Directory for downloaded historical data in CSV format

download_csv_row_data_agent_csv_path = "/var/log/czentrix/TE_dashboard/agent_state_analysis/download_csv_row_data/agent_historical_data/"


download_csv_live_current_row_data = '/var/log/czentrix/TE_dashboard/download_csv_row_data/live_data/'
# Directory for live or near-real-time downloaded data in CSV format

operator_csv_file_path = "/var/log/czentrix/operator_xls/operator.xlsx"
# Path to a specific Excel file, possibly containing operator mappings or performance data

campaign_detailed_call_report_csv_file_path = '/var/log/czentrix/TE_dashboard/campaign_detailed_call_report_csv/row_data/'
# Path for storing campaign-level call detail CSV reports

# ------------------ Filter & Lock File Paths ------------------

filter_path = "/var/log/czentrix/TE_dashboard/filter/"
# Directory for storing files used in filtering datasets (e.g., user-defined filters)

acquire_lock_file = 'acquire_lock.lock'
# File name used to create a lock file for general process locking

yearly_acquire_lock_file = 'yearly_acquire_lock.lock'
# Lock file name specifically for yearly job protection

file_path = '/var/log/czentrix/TE_dashboard/lock_files/'
# Base directory for all lock-related files to avoid process overlap

yearly_file_path = '/var/log/czentrix/TE_dashboard/lock_files/'
# Separate or reused path for yearly lock file storage (could be made distinct if needed)
