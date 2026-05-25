#!/bin/bash

# Navigate to the specified directory
cd /Czentrix/apps/TE_dashboard_backend/

# Store the current directory's virtual environment binary path in a variable
cdir="$(pwd)/venv/bin/"

# Print the virtual environment directory for debugging purposes
echo "Virtual environment directory: $cdir"

# Create a virtual environment named 'venv' using Python 3
echo "Creating virtual environment..."
python3 -m venv venv
# Alternatively, create the virtual environment using a specific Python interpreter
virtualenv venv -p /opt/python3.6.7/bin/python3
echo "Virtual environment created."

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install the required packages listed in requirements.txt
echo "Installing requirements..."
pip install -r requirements.txt
echo "Requirements installed."

# Define the path for the main data directory
main_data_path_dit='/var/log/czentrix/TE_dashboard/'

# Create the main data directory if it doesn't exist
mkdir -p "$main_data_path_dit"

# Confirm that the config.toml file has been created successfully
echo "Config.toml file has been created successfully."

# =====================================================
# ADD CRON JOBS (SAFE METHOD)
# =====================================================

echo "Adding cron jobs..."

# ---- Job 1 ----
cron_job1="10 00 * * * /Czentrix/apps/TE_dashboard_backend/venv/bin/python /Czentrix/apps/TE_dashboard_backend/acquire_lock.py"

# ---- Job 2 ----
cron_job2="10 00 * * * /Czentrix/apps/TE_dashboard_backend/venv/bin/python /Czentrix/apps/TE_dashboard_backend/delete_365days_old_data.py"

# ---- Job 3 ----
cron_job3="*/5 * * * * /Czentrix/apps/TE_dashboard_backend/venv/bin/python /Czentrix/apps/TE_dashboard_backend/service_check.py"

# # ---- Job 4 ----
cron_job4="10 00 * * * /usr/bin/systemctl restart live-data.service 2>/dev/null;"

# Function to safely add cron
add_cron_job() {
    crontab -l 2>/dev/null | grep -F "$1" > /dev/null

    if [ $? -eq 0 ]; then
        echo "Already exists: $1"
    else
        (crontab -l 2>/dev/null; echo "$1") | crontab -
        echo "Added: $1"
    fi
}

# Add all jobs
add_cron_job "$cron_job1"
add_cron_job "$cron_job2"
add_cron_job "$cron_job3"
add_cron_job "$cron_job4"

echo "All cron jobs added successfully."
echo "Setup completed."
