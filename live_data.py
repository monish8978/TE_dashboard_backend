"""
Live data processing script

- Connects to MySQL
- Fetches current report data for today
- Saves it to campaign-specific CSV files
- Deletes yesterday's file
- Deletes any file with a date in the future
- Runs compute layer + data layer in parallel
"""

# ------------------ Import Config File ------------------
from settings import mysql_info, download_csv_live_current_row_data, live_data_log_path
from compute_layer_cmp_live import main as cmp_compute_data
from data_layer_cmp_live import main as cmp_data_layer_data
from compute_layer_function_agent_live import main as main_compute_layer_function_agent
from compute_layer_agent_live import main as main_filter_data_agent
from data_layer_agent_live import main as main_dump_data_agent

# ------------------ Import Modules ------------------
from datetime import datetime, timedelta
import pandas as pd
import traceback
import pymysql
import logging
import threading
import warnings
import time
import os

# ------------------ Setup ------------------
warnings.filterwarnings("ignore")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s',
    level=logging.INFO,
    filename=live_data_log_path
)

log = logging.getLogger('__main__')

# Thread safety (future use)
lock = threading.Lock()


# ==========================================================
#                    DB CONNECTION
# ==========================================================

def sql_conn():
    db = None
    cur = None

    try:
        db = pymysql.connect(
            host=mysql_info['host'],
            user=mysql_info['user'],
            password=mysql_info['password'],
            db=mysql_info['database']
        )
        cur = db.cursor()

    except Exception as err:
        log.error("Not able to connect to MySQL. Reason: " + str(err))
        traceback.print_exc()

    return db, cur


# ==========================================================
#                    DATE HELPER
# ==========================================================

def get_date():
    try:
        today = datetime.now()
        yesterday_date = today.date() - timedelta(days=1)
        today_date = today.date()
        return today_date, yesterday_date

    except Exception as err:
        log.error(str(err))
        traceback.print_exc()


# ==========================================================
#            FETCH DATA + SAVE CSV (THREAD 1)
# ==========================================================

def current_report_te_data(mydb, today_date, yesterday_date):

    try:
        df = pd.read_sql(f"""
            SELECT agent_id, agent_name, campaign_id, campaign_name, wrapup_time, call_duration, wait_time,
                   call_status_disposition, next_call_time, campaign_type, q_enter_time, q_leave_time,
                   call_start_date_time, call_end_date_time, skills, list_name
            FROM current_report
            WHERE date(call_start_date_time) = '{today_date}'
        """, con=mydb)

        mydb.commit()

        for campaign_name, group_df in df.groupby('campaign_name'):

            if not group_df.empty:

                directory_path = os.path.join(download_csv_live_current_row_data, campaign_name)

                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)

                # Save today's CSV
                today_file_path = os.path.join(directory_path, f"{today_date}.csv")
                group_df.to_csv(today_file_path, index=False)

                log.info(f"Saved today's CSV for campaign '{campaign_name}': {today_file_path}")

                # Delete yesterday file
                yesterday_file_path = os.path.join(directory_path, f"{yesterday_date}.csv")

                if os.path.exists(yesterday_file_path):
                    os.remove(yesterday_file_path)
                    log.info(f"Deleted yesterday file: {yesterday_file_path}")

                # Delete invalid/future files
                for filename in os.listdir(directory_path):

                    if filename.endswith(".csv"):
                        try:
                            file_date = datetime.strptime(filename.replace(".csv", ""), "%Y-%m-%d").date()

                            if file_date < today_date:
                                file_path = os.path.join(directory_path, filename)
                                os.remove(file_path)
                                log.info(f"Deleted future-dated file: {file_path}")

                        except ValueError:
                            log.warning(f"Invalid filename skipped: {filename}")

    except Exception as err:
        log.error("Error in current_report_te_data: " + str(err))
        traceback.print_exc()


# ==========================================================
#            COMPUTE + DATA LAYER (THREAD 2)
# ==========================================================

def cmp_dash_live_data():
    try:
        cmp_compute_data()
        cmp_data_layer_data()

    except Exception as err:
        log.error("Error in cmp_dash_live_data: " + str(err))
        traceback.print_exc()

def agent_dash_live_data():
    try:
        main_dump_data_agent()
        main_filter_data_agent()
        main_compute_layer_function_agent()
    except Exception as err:
        log.error("Error in cmp_dash_live_data: " + str(err))
        traceback.print_exc()


# ==========================================================
#                    MAIN LOOP
# ==========================================================

def main():

    mydb, mycursor = sql_conn()

    while True:

        # Reconnect if connection is lost
        try:
            mydb.ping(reconnect=True)
        except:
            mydb, mycursor = sql_conn()

        if mydb:

            today_date, yesterday_date = get_date()

            # Thread 1 -> Save CSV
            t1 = threading.Thread(
                target=current_report_te_data,
                args=(mydb, today_date, yesterday_date)
            )

            # Thread 2 -> Compute + Data Layer
            t2 = threading.Thread(
                target=cmp_dash_live_data
            )

            t3 = threading.Thread(
                target=agent_dash_live_data
            )

            t1.start()
            t1.join()

            t2.start()
            t2.join()

            t3.start()
            t3.join()

        else:
            log.error("MySQL connection not established. Retrying...")

        # Wait 3 minutes
        time.sleep(180)


# ==========================================================
#                    START SCRIPT
# ==========================================================

if __name__ == "__main__":
    main()

