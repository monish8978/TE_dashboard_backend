"""
        import settings file
"""
from settings import mysql_info,common_csv_cmp_file_path,data_layer_log_path,live_day_count
"""
        import modules
"""
import pymysql
import pandas as pd
from pathlib import Path
import time
import os
from datetime import datetime,timedelta
import traceback
import logging
import threading
import warnings
warnings.filterwarnings("ignore")


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
        yesterday_date = today.date() - timedelta(days=live_day_count)

        # Format the datetime object to "YYYY_MM" string
        year_month = yesterday_date.strftime("%Y_%m")
        return yesterday_date,year_month


def dump_data(mydb,yesterday_date,year_month):
        # create directory
        if not os.path.exists(common_csv_cmp_file_path):
                os.makedirs(common_csv_cmp_file_path)
        try:
                # file name
                filename =  f"day_{yesterday_date}.csv"
                # sql query
                query = f"select * from current_report where DATE(call_start_date_time) = '{yesterday_date}'"
                df = pd.read_sql(query,con=mydb)
                # create csv file
                if not os.path.exists(f"{common_csv_cmp_file_path}{filename}"):
                        if not df.empty:
                                df.to_csv(f"{common_csv_cmp_file_path}{filename}",index=False)
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def main():
        mydb = sql_conn()
        yesterday_date,year_month = date_time()
        dump_data(mydb,yesterday_date,year_month)


