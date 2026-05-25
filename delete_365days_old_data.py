import os
import datetime
import logging
from settings import download_csv_row_data, campaign_detailed_call_report_csv_file_path,delete_old_csv_files

# ------------------ Logging Configuration ------------------

# Define the name of the log file where logs will be stored
log_file = delete_old_csv_files

# Set up logging to file with INFO level and a consistent format
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Also log to the console in addition to the file
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# ------------------ Date Calculations ------------------

# Get yesterday's date (used to avoid dealing with partially written files from today)
yesterday = datetime.date.today() - datetime.timedelta(days=1)

# Define cutoff date for deletion: 365 days before yesterday
cutoff_date = yesterday - datetime.timedelta(days=365)

# ------------------ Function: delete_old_files_telephony_data ------------------

def delete_old_files_telephony_data():
    """
    Deletes telephony CSV files older than 365 days from the telephony data directory.
    Each campaign has its own subdirectory, and CSV files are named by date (YYYY-MM-DD.csv).
    """
    # logging.info("Starting deletion of old telephony data files.")

    # Iterate through each campaign subdirectory
    for campaign_dir in os.listdir(download_csv_row_data):
        campaign_path = os.path.join(download_csv_row_data, campaign_dir)

        if os.path.isdir(campaign_path):  # Ensure it's a directory
            for filename in os.listdir(campaign_path):
                if filename.endswith(".csv"):  # Only consider CSV files
                    try:
                        # Extract the date from the filename (expects YYYY-MM-DD.csv format)
                        file_date = datetime.datetime.strptime(filename.replace(".csv", ""), "%Y-%m-%d").date()

                        # Delete file if it's older than the cutoff date
                        if file_date < cutoff_date:
                            file_path = os.path.join(campaign_path, filename)
                            os.remove(file_path)
                            logging.info(f"Deleted telephony file: {file_path}")
                    except ValueError:
                        # If filename doesn't match the expected date format, skip it
                        logging.warning(f"Skipped invalid telephony file: {filename}")

    # logging.info("Completed deletion of old telephony data files.")

# ------------------ Function: delete_old_files_campaign_details_data ------------------

def delete_old_files_campaign_details_data():
    """
    Deletes campaign detail report CSV files older than 365 days from the campaign report directory.
    Each campaign has its own subdirectory, and CSV files are named by date (YYYY-MM-DD.csv).
    """
    # logging.info("Starting deletion of old campaign detail report files.")

    # Iterate through each campaign subdirectory
    for campaign_dir in os.listdir(campaign_detailed_call_report_csv_file_path):
        campaign_path = os.path.join(campaign_detailed_call_report_csv_file_path, campaign_dir)

        if os.path.isdir(campaign_path):  # Ensure it's a directory
            for filename in os.listdir(campaign_path):
                if filename.endswith(".csv"):  # Only consider CSV files
                    try:
                        # Extract the date from the filename (expects YYYY-MM-DD.csv format)
                        file_date = datetime.datetime.strptime(filename.replace(".csv", ""), "%Y-%m-%d").date()

                        # Delete file if it's older than the cutoff date
                        if file_date < cutoff_date:
                            file_path = os.path.join(campaign_path, filename)
                            os.remove(file_path)
                            logging.info(f"Deleted campaign detail file: {file_path}")
                    except ValueError:
                        # If filename doesn't match the expected date format, skip it
                        logging.warning(f"Skipped invalid campaign detail file: {filename}")

    # logging.info("Completed deletion of old campaign detail report files.")

# ------------------ Script Entry Point ------------------

if __name__ == "__main__":
    # Log the start of the script execution
    # logging.info("Starting CSV file cleanup process.")

    # Call deletion functions for both datasets
    delete_old_files_telephony_data()
    delete_old_files_campaign_details_data()

    # Log the completion of the script
    # logging.info("CSV file cleanup process completed.")
