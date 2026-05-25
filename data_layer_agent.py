"""
        import settings file
"""
from settings import mysql_info,common_csv_file_path_agent,data_layer_log_path,day_count,data_layer_log_path
"""
        import modules
"""
from datetime import datetime,timedelta
import pandas as pd
import traceback
import threading
import logging
import pymysql
import os
import warnings
warnings.filterwarnings("ignore")

# create log diroctry
if not os.path.exists(data_layer_log_path):
        os.makedirs(data_layer_log_path)

logname = data_layer_log_path
logging.basicConfig(filename=logname,level=logging.DEBUG)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
fh = logging.FileHandler(logname,mode='a+')
formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)5s %(levelname)4s - %(lineno)3s - %(message)s")
fh.setFormatter(formatter)
log.addHandler(fh)

log.info("Loading....")

log = logging.getLogger('__main__')
lock = threading.Lock()

def sql_conn():

        """
                Handing for sql connection.
                Args:-
                        There is no need to use any args just use the configuration variable from config file.
                Return:
                        db:- Return database object after crete database connection
        """
        db = ""
        cur = ""
        try:
                db = pymysql.connect(host=mysql_info['host'],user=mysql_info['user'],password= mysql_info['password'],db=mysql_info['database'])
                # Create a connection to the MySQL database
        except Exception as err:
                log.error("Not Able to connect mysql reason is "+str(err))
                traceback.print_exc()
        return db


def date_time():
        today = datetime.now()
        yesterday_date = today.date() - timedelta(days=day_count)

        # Format the datetime object to "YYYY_MM" string
        year_month = yesterday_date.strftime("%Y_%m")
        return yesterday_date,year_month


def dump_data(mydb,yesterday_date,year_month):
        # create diroctry
        if not os.path.exists(common_csv_file_path_agent):
                os.makedirs(common_csv_file_path_agent)
        try:
                # current report file name
                detailed_call_report_filename =  f"detailed_call_report_{yesterday_date}.csv"
                # agent state analysis file name
                agent_filename =  f"agent_state_analysis_{yesterday_date}.csv"
                # filename =  f"day_{yesterday_date}.csv"

                # sql query for current report
                detailed_query = f"select agent_id,agent_name,campaign_id,campaign_name,wrapup_time,call_duration,wait_time,call_status_disposition,next_call_time,campaign_type,agent_id,q_enter_time,q_leave_time,call_start_date_time,call_end_date_time,ringstart_time,ringend_time,hold_time from {year_month} where DATE(call_start_date_time) = '{yesterday_date}'"
                detailed_df = pd.read_sql(detailed_query,con=mydb)

                # sql query for agent state analysis current report
                agent_query = f"select * from agent_state_analysis_{year_month} where DATE(call_start_date_time) = '{yesterday_date}'"
                agent_df = pd.read_sql(agent_query,con=mydb)

                # create csv file current report
                if not detailed_df.empty:
                        detailed_df.to_csv(f"{common_csv_file_path_agent}{detailed_call_report_filename}",index=False)

                # create csv file agent state analysis current report
                if not agent_df.empty:
                        agent_df.to_csv(f"{common_csv_file_path_agent}{agent_filename}",index=False)
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def main():
        mydb = sql_conn()
        yesterday_date,year_month = date_time()
        dump_data(mydb,yesterday_date,year_month)

