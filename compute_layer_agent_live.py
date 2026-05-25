from settings import common_csv_file_path_agent,download_csv_row_data_agent,compute_layer_log_path,live_day_count
from datetime import datetime,timedelta
import pandas as pd
import traceback
import threading
import logging
import os
import warnings
warnings.filterwarnings("ignore")

logname = compute_layer_log_path
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

def csv_name():
      try:
            today = datetime.now()
            yesterday = today - timedelta(days=live_day_count)
            yesterday_date = yesterday.strftime('%Y-%m-%d')

            file_name = f"{common_csv_file_path_agent}detailed_call_report_{yesterday_date}.csv"
            return file_name,yesterday_date
      except Exception as err:
            log.error(str(err))
            traceback.print_exc()


def read_file(file_name):
    try:
      if os.path.exists(file_name):
            df = pd.read_csv(file_name)
            return df
    except Exception as err:
           log.error(str(err))
           traceback.print_exc()


def campaign_name_df(yesterday_date,campaign_df):
       try:
            l = []
            if campaign_df is not None:
                  campaign_name = set(campaign_df['campaign_name'])
                  for c in campaign_name:
                        data = c
                        l.append(data)
                  df = pd.DataFrame(l)
                  directory_path = f'{download_csv_row_data_agent}/campaignname/'

                  if not os.path.exists(directory_path):
                        os.makedirs(directory_path)

                  a = df.to_csv(f'{download_csv_row_data_agent}/campaignname/{yesterday_date}.csv',index=False)
                  return campaign_name
       except Exception as err:
            log.error(str(err))
            traceback.print_exc()


def create_csv_filter(yesterday_date,campaign_name,campaign_df):
      try:
            if campaign_df is not None:
                  for c in campaign_name:
                        df = campaign_df[campaign_df['campaign_name'] == c]
                        overall_wise_call = df[["campaign_id","campaign_name","wrapup_time","call_duration","wait_time","call_status_disposition","next_call_time","campaign_type","agent_id","q_enter_time","q_leave_time","call_start_date_time","call_end_date_time","ringstart_time","ringend_time","hold_time","agent_name"]]

                        directory_path = f'{download_csv_row_data_agent}/{c}'

                        if not os.path.exists(directory_path):
                              os.makedirs(directory_path)
                        a = overall_wise_call.to_csv(f'{directory_path}/{yesterday_date}.csv')
      except Exception as err:
            log.error(str(err))
            traceback.print_exc()


def main():
      file_name,yesterday_date = csv_name()
      campaign_df = read_file(file_name)
      campaign_name = campaign_name_df(yesterday_date,campaign_df)
      create_csv_filter(yesterday_date,campaign_name,campaign_df)
