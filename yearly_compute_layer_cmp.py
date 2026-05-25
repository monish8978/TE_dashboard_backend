"""
        import settings file
"""
from settings import common_csv_cmp_file_path,operator_csv_file_path,campaign_detailed_call_report_csv_file_path,compute_layer_log_path,start_count,end_count
"""
        import modules
"""
from datetime import datetime,timedelta
import pandas as pd
import traceback
import threading
import logging
import os
import re


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
            file_name_list = []
            today = datetime.now()
            for tmp_day_count in range(start_count,end_count):
                  yesterday = today - timedelta(days=tmp_day_count)
                  yesterday_date = yesterday.strftime('%Y-%m-%d')

                  file_name = f"{common_csv_cmp_file_path}day_{yesterday_date}.csv"
                  file_name_list.append(file_name)
            return file_name_list
      except Exception as err:
            log.error(str(err))
            traceback.print_exc()

def series_df():
    try:
        df_act = pd.read_excel(operator_csv_file_path,engine='openpyxl')
        df_act = df_act.dropna(axis=1, how='all')
        df_act.rename(columns=lambda x : x.replace(' ','_').lower(),inplace = True)
        df_act['series'] = df_act['series'].astype(str)
        return df_act
    except Exception as err:
        log.error(str(err))
        traceback.print_exc()


def read_file(file_name_list):
    try:
      for file_name in file_name_list:
            # Define the regular expression pattern for the date (YYYY-MM-DD)
            pattern = r'\d{4}-\d{2}-\d{2}'

            # Search for the pattern in the input string
            match = re.search(pattern, file_name)

            # Extract and print the date if a match is found
            if match:
                  yesterday_date = match.group(0)
            else:
                  log.error("No date found in the input string")
            df1 = series_df()
            if os.path.exists(file_name):
                  df2 = pd.read_csv(file_name)
                  df2 = df2.dropna(axis=1,how='all')
                  # rename columns and set new columns
                  df2.rename(columns=lambda x : x.replace(' ','_').lower(),inplace = True)
                  try:
                      df2['call_start_date_time'] = pd.to_datetime(df2['call_start_date_time'])
                  except:
                      df2['call_start_date_time'] = df2['call_start_date_time'].replace("0", "1970-01-01")
                      df2 = df2[df2['call_start_date_time'] != "0"]
                      df2['call_start_date_time'] = pd.to_datetime(df2['call_start_date_time'])
                  df2['date'] = df2['call_start_date_time'].dt.date
                  df2['hour'] = df2['call_start_date_time'].dt.hour

                  # Check if all values in 'Column1' are zero
                  is_all_zeros = (df2['hour'] == 0).all()
                  if is_all_zeros == True:
                        df2['time'] = "00:00:01"
                  else:
                        df2['time'] = pd.to_timedelta(df2['hour'], unit='H')
                        df2['time'] = df2['time'].astype(str).str.split().str[-1]

                  df2['cust_ph_no'] = df2['cust_ph_no'].astype(str)
                  df2['date'] = df2['date'].astype(str)
                  try:
                      df2['datetime_combined'] = pd.to_datetime(df2['date'] + ' ' + df2['time'])
                  except:
                      df2['datetime_combined'] = pd.NaT

                  # updating phone number section
                  def update_ph_no(ph_no):
                  #     df1 = reading_excel_and_cleaning_data()
                        if len(ph_no) > 10 and ph_no.startswith('+91'):
                                    return ph_no[3:]
                        elif len(ph_no) > 10 and ph_no.startswith('91'):
                              return ph_no[2:]
                        else:
                              return ph_no

                  def convert_to_int(value):
                        try:
                                    return int(float(value))
                        except (ValueError, TypeError):
                                    return value

                  # Apply the function to the 'series' column
                  df1['series'] = df1['series'].apply(convert_to_int)

                  df2['actual_number'] = df2['cust_ph_no'].apply(update_ph_no)
                  df2['first4'] = df2['actual_number'].str[:4]
                  df1['series'] = df1['series'].astype(str)

                  # merging all dataframe
                  #=======================================#
                  merged_df = df2.merge(df1,left_on='first4',right_on='series',how='left')

                  # drop columns
                  columns_to_drop = ['first4', 'series']
                  merged_df.drop(columns=columns_to_drop,inplace=True)

                  operator_name = {'AT':'Airtel','VI':'Vodafone Idea','CG':'BSNL/MTNL','RJ':'Reliance Jio'}
                  region_name = {'AP':'Andhra Pradesh','AS':'Assam','BR':'Bihar & Jharkhand','DL':'Delhi','GJ':'Gujarat','HP':'Himachal Pradesh',
                                    'HR':'Haryana','JK':'Jammu and Kashmir','KL':'Kerala & Lakshadweep','KA':'Karnataka','KO':'Kolkata','MH':'Maharashtra & Goa',
                                    'MP':'Madhya Pradesh & Chhattisgarh','MU':'Mumbai','NE':'North East','OR':'Odisha','PB':'Punjab','RJ':'Rajasthan',
                                    'TN':'Tamil Nadu','UE':'UP(East)','UW':'UP(West)','WB':'West Bengal'}

                  def operator_update(operator):
                        if operator in operator_name:
                                    return operator_name[operator]
                        else:
                                    return "Others"

                  def region_wise(region):
                        if region in region_name:
                                    return region_name[region]
                        else:
                                    return "Others"

                  merged_df['operator'] = merged_df['operator'].apply(operator_update)
                  merged_df['circle'] = merged_df['circle'].apply(region_wise)
                  campaign_df = merged_df[['date','campaign_name','dialer_type','campaign_type','operator','circle','call_status_disposition','datetime_combined','hour','time','call_duration']]

                  try:
                        l = []
                        campaign_name = set(campaign_df['campaign_name'])
                        for c in campaign_name:
                              data = c
                              l.append(data)
                        df = pd.DataFrame(l)
                        directory_path = f'{campaign_detailed_call_report_csv_file_path}campaignname/'

                        if not os.path.exists(directory_path):
                              os.makedirs(directory_path)

                        a = df.to_csv(f'{directory_path}{yesterday_date}.csv',index=False)

                        try:
                              for c in campaign_name:
                                    df = campaign_df[campaign_df['campaign_name'] == c]
                                    overall_wise_call = df[['date','campaign_name','dialer_type','campaign_type','operator','circle','call_status_disposition','datetime_combined','hour','time','call_duration']]
                                    directory_path = f'{campaign_detailed_call_report_csv_file_path}{c}'

                                    if not os.path.exists(directory_path):
                                          os.makedirs(directory_path)
                                    a = overall_wise_call.to_csv(f'{directory_path}/{yesterday_date}.csv')
                        except Exception as err:
                              log.error(str(err))
                              traceback.print_exc()

                  except Exception as err:
                        log.error(str(err))
                        traceback.print_exc()
    except Exception as err:
           log.error(str(err))
           traceback.print_exc()


def delete_csv_file(file_name_list):
      try:
            for file_name in file_name_list:
                  if os.path.exists(file_name):
                        #print(file_name)
                        os.remove(file_name)
      except Exception as err:
            log.error(str(err))
            traceback.print_exc()



def main():
      file_name_list = csv_name()
      read_file(file_name_list)
      delete_csv_file(file_name_list)


if __name__ == "__main__":
        main()