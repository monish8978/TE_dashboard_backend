"""
        import settings file
"""
from settings import mysql_info,common_csv_cmp_file_path,data_layer_log_path,start_count,end_count
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
                log.error("Not Able to connect mysql reason is "+str(e))
                traceback.print_exc()
        return db


def date_time():
        today = datetime.now()
        date_list = []
        for tmp_day_count in range(start_count,end_count):
                yesterday_date = today.date() - timedelta(days=tmp_day_count)
                #print(yesterday_date)
                date_list.append(yesterday_date)
        return date_list

def dump_data(mydb,date_list):
        # create diroctry
        if not os.path.exists(common_csv_cmp_file_path):
                os.makedirs(common_csv_cmp_file_path)
        try:
                for yesterday_date in date_list:
                        yesterday_date = str(yesterday_date)
                        # Convert string to datetime object
                        date_obj = datetime.strptime(yesterday_date, "%Y-%m-%d")

                        # Extract year and month
                        year_month = date_obj.strftime("%Y_%m")
                        # file name
                        filename =  f"day_{yesterday_date}.csv"
                        # sql query
                        ""
                        query = f"select * from {year_month} where DATE(call_start_date_time) = '{yesterday_date}'"
                        df = pd.read_sql(query,con=mydb)

                        # create csv file
                        if not df.empty:
                                df.to_csv(f"{common_csv_cmp_file_path}{filename}",index=False)
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def main():
        mydb = sql_conn()
        date_list = date_time()
        dump_data(mydb,date_list)


if __name__ == "__main__":
        main()
