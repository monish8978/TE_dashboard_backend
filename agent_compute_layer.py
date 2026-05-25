"""
import settings file
"""
from settings import compute_layer_log_path,download_csv_row_data_agent_csv_path,download_csv_row_data_agent
"""
        import modules
"""
from datetime import datetime,timedelta
import pandas as pd
import traceback
import threading
import logging
import warnings
import fnmatch
import os

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


# Function to get today's date
def get_date():
    try:
        today_date = datetime.now().strftime('%Y-%m-%d')
        return today_date
    except Exception as err:
        log.error(str(err))
        traceback.print_exc()

def read_csv_files(selected_campaign_name,start_date,end_date,today_date):
        try:
                # Use datetime.combine to convert date to datetime
                start_date = datetime.combine(start_date, datetime.min.time())
                end_date = datetime.combine(end_date, datetime.min.time())

                # today_date = datetime.combine(today_date, datetime.min.time())

                today_date = datetime.strptime(today_date, "%Y-%m-%d")

                if start_date == today_date == end_date:
                        # csv_file_path
                        folder_path = f"{download_csv_row_data_agent_csv_path}{selected_campaign_name}/"
                else:
                        # csv_file_path
                        folder_path = f"{download_csv_row_data_agent_csv_path}{selected_campaign_name}/"

                # Initialize an empty DataFrame to store the concatenated data
                combined_df = pd.DataFrame()

                # List all files in the specified folder
                all_files = []
                for root, dirs, files in os.walk(folder_path):
                        for file in files:
                                if fnmatch.fnmatch(file, '*.csv'):
                                                all_files.append(os.path.join(root, file))

                # Filter files based on their file date
                for file_path in all_files:
                        file_date_str = file_path.split("/")[-1].split(".")[0]
                        file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                        if start_date <= file_date <= end_date:
                                df = pd.read_csv(file_path)
                                # Append the DataFrame to the combined DataFrame
                                combined_df = pd.concat([combined_df, df], ignore_index=True)

                if combined_df.empty:
                        # Create an empty DataFrame with columns
                        columns = ['agent_id', 'agent_name', 'campaign_id', 'campaign_name', 'wrapup_time', 'call_duration', 'wait_time', 'call_status_disposition', 'next_call_time', 'campaign_type', 'q_enter_time', 'q_leave_time', 'call_start_date_time', 'call_end_date_time']

                        combined_df = pd.DataFrame(columns=columns)
                return combined_df
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def read_csv_files_current_report(selected_campaign_name,start_date,end_date,today_date):
    try:
        # Use datetime.combine to convert date to datetime
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.min.time())

        today_date = datetime.strptime(today_date, "%Y-%m-%d")

        if start_date == today_date == end_date:
                # csv_file_path
                folder_path = f"{download_csv_row_data_agent}{selected_campaign_name}/"
        else:
                # csv_file_path
                folder_path = f"{download_csv_row_data_agent}{selected_campaign_name}/"

        # Initialize an empty DataFrame to store the concatenated data
        combined_df = pd.DataFrame()

        # List all files in the specified folder
        all_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if fnmatch.fnmatch(file, '*.csv'):
                    all_files.append(os.path.join(root, file))

        # Filter files based on their file date
        for file_path in all_files:
            file_date_str = file_path.split("/")[-1].split(".")[0]
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
            if start_date <= file_date <= end_date:
                df = pd.read_csv(file_path)
                # Append the DataFrame to the combined DataFrame
                combined_df = pd.concat([combined_df, df], ignore_index=True)

        if combined_df.empty:
            # Create an empty DataFrame with columns
            columns = ['campaign_id', 'campaign_name', 'wrapup_time','call_duration', 'wait_time', 'call_status_disposition','next_call_time', 'campaign_type', 'agent_id', 'q_enter_time','q_leave_time','call_start_date_time','call_end_date_time','ringstart_time','ringend_time','hold_time','agent_name']

            combined_df = pd.DataFrame(columns=columns)

        combined_df.rename(columns=lambda x: x.replace(' ', '_').lower(), inplace=True)

        # adding new column 'date' and 'month' in dataset.
        combined_df['date_time'] = pd.to_datetime(combined_df['call_start_date_time'])
        combined_df['day_name'] = combined_df['date_time'].dt.strftime('%d')
        combined_df['month_name'] = combined_df['date_time'].dt.month_name()
        combined_df['months'] = combined_df['date_time'].dt.month
        combined_df['days'] = combined_df['date_time'].dt.day
        # Extract the hour
        combined_df['hour'] = combined_df['date_time'].dt.hour

        #----------------------------ringtime calculations-----------------#
        combined_df['ringstart_time'] = pd.to_datetime(combined_df['ringstart_time'], errors='coerce')
        combined_df['ringend_time'] = pd.to_datetime(combined_df['ringend_time'], errors='coerce')
        combined_df['ring_duration(sec)'] = (combined_df['ringend_time'] - combined_df['ringstart_time']).dt.total_seconds()
        combined_df['ring_duration(sec)'] = combined_df['ring_duration(sec)'].fillna(0)

         #---------actual talktime calculations---------------#
        combined_df['Agent_Talk_Time'] = combined_df['call_duration'] -  combined_df['ring_duration(sec)'] - combined_df['hold_time']

        #----------------------queue time calculations-----------#
        combined_df['q_leave_time'] = pd.to_datetime(combined_df['q_leave_time'], errors='coerce')
        combined_df['q_enter_time'] = pd.to_datetime(combined_df['q_enter_time'], errors='coerce')
        combined_df['Agent_Queue_Time'] = (combined_df['q_leave_time']- combined_df['q_enter_time']).dt.total_seconds()

        a_date = combined_df
        # average call duration scoring.
        avg_ct = a_date['call_duration'].mean()

        def avg_call_duration(agent_call_d):
            if agent_call_d >= avg_ct:
                return 1 * 9.25
            elif agent_call_d == avg_ct:
                return 1 * 7.25
            else:
                return 1 * 4.25

        # # average queue_time scoring
        avg_qt = a_date['Agent_Queue_Time'].mean()
        # avg_qt = avg_qt.round(2)

        def avg_queue_time(agent_qt):
            if agent_qt >= avg_qt:
                return 1* 9.25
            elif agent_qt == avg_qt:
                return 1 * 7.5
            else:
                return 1 * 4.25

        # average wrapup time
        avg_wut = a_date['wrapup_time'].mean()
        # avg_wut = avg_wut.round(2)

        def avg_wrapup_time(agent_wut):
            if agent_wut >= avg_wut:
                return 1 * 9.25
            elif agent_wut == avg_wut:
                return 1 * 7.5
            else:
                return 1 * 4.25

        # # average average wait time scoring
        avg_wt = a_date['wait_time'].mean()
        # avg_wt = avg_wt.round(2)

        def avg_wait_duration(agent_wait_d):
            if agent_wait_d >= avg_wt:
                return 2 * 9.25
            elif agent_wait_d == avg_wt:
                return 2 * 7.5
            else:
                return 2 * 4.25

        # average talktime scoring
        avg_tt = a_date['Agent_Talk_Time'].mean()
        # avg_tt = avg_tt.round(2)

        def avg_talktime_duration(agent_talk_d):
            if agent_talk_d >= avg_tt:
                return 2 * 9.25
            elif agent_talk_d == avg_tt:
                return 2 * 7.5
            else:
                return 2 * 4.25

        a_date['Score'] = a_date['call_duration'].apply(avg_call_duration)

        a_date['Score'] += a_date['Agent_Queue_Time'].apply(avg_queue_time)
        a_date['Score'] += a_date['wrapup_time'].apply(avg_wrapup_time)
        a_date['Score'] += a_date['wait_time'].apply(avg_wait_duration)
        a_date['Score'] += a_date['Agent_Talk_Time'].apply(avg_talktime_duration)

        return a_date
    except Exception as err:
            log.error(str(err))
            traceback.print_exc()

def eda_call_status(df_act):
    try:
        if not df_act.empty:
            tmp_df = df_act.groupby(['agent_id','day_name'])['Score'].sum().reset_index()

            # Apply Min-Max normalization to the 'Score' column
            min_score = tmp_df['Score'].min()
            max_score = tmp_df['Score'].max()

            tmp_df['Normalized_Score'] = (tmp_df['Score'] - min_score) / (max_score - min_score) * 100

            avg_score = df_act['Score'].mean()
            avg_score = avg_score.round(2)
        else:
            avg_score = 0
        return avg_score
    except Exception as err:
        log.error(str(err))
        traceback.print_exc()


def avg_prod_hours(prod_df):
    if not prod_df.empty:
        prod_df = prod_df[['agent_id','agent_name','Productive_Hours']]
        # Ensure that the Productive_Hours column is of type string
        prod_df['Productive_Hours'] = prod_df['Productive_Hours'].astype(str)

        # Extracting the time part from the Productive_Hours column and converting to hours
        prod_df['Total_Hours'] = prod_df['Productive_Hours'].apply(
            lambda x: int(x.split(' ')[-1].split(':')[0]) +
                    int(x.split(' ')[-1].split(':')[1]) / 60 +
                    int(x.split(' ')[-1].split(':')[2]) / 3600
        )
        avg_productive_hour = prod_df['Total_Hours'].mean()

        total_seconds = avg_productive_hour * 3600
        td = timedelta(seconds=total_seconds)
        # Extract hours, minutes, and seconds from the timedelta object
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        avg_productive_hour = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        avg_productive_hour = '00:00:00'
    return avg_productive_hour

def avg_unprod_hours(unprod_df):
    if not unprod_df.empty:
        unprod_df = unprod_df[['agent_id','agent_name','Unproductive_Hours']]
        # Ensure that the Productive_Hours column is of type string
        unprod_df['Unproductive_Hours'] = unprod_df['Unproductive_Hours'].astype(str)

        # Extracting the time part from the Productive_Hours column and converting to hours
        unprod_df['Total_Hours'] = unprod_df['Unproductive_Hours'].apply(
            lambda x: int(x.split(' ')[-1].split(':')[0]) +
                    int(x.split(' ')[-1].split(':')[1]) / 60 +
                    int(x.split(' ')[-1].split(':')[2]) / 3600
        )
        avg_unproductive_hour = unprod_df['Total_Hours'].mean()

        total_seconds = avg_unproductive_hour * 3600
        td = timedelta(seconds=total_seconds)
        # Extract hours, minutes, and seconds from the timedelta object
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        avg_unproductive_hour = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        avg_unproductive_hour = '00:00:00'
    return avg_unproductive_hour

def avg_wait_time(waittime_df):
    if not waittime_df.empty:
        waittime_df = waittime_df[['agent_id','agent_name','Agent_Wait_Time']]
        avg_wait_time_sec = waittime_df['Agent_Wait_Time'].mean()

        td = timedelta(seconds=avg_wait_time_sec)
        # Extract hours, minutes, and seconds from the timedelta object
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        avg_wait_time_sec = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
         avg_wait_time_sec = '00:00:00'
    return avg_wait_time_sec

def avg_wrapup_time(wrapup_df):
    if not wrapup_df.empty:
        wrapup_df = wrapup_df[['agent_id','agent_name','Agent_Wrapup_Time']]
        avg_wrapup_time_sec = wrapup_df['Agent_Wrapup_Time'].mean()

        td = timedelta(seconds=avg_wrapup_time_sec)
        # Extract hours, minutes, and seconds from the timedelta object
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        avg_wrapup_time_sec = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
         avg_wrapup_time_sec = '00:00:00'
    return avg_wrapup_time_sec

def avg_call_duration(call_duration_df):
    if not call_duration_df.empty:
        call_duration_df = call_duration_df[['agent_id','agent_name','Agent_Call_Duration']]
        avg_call_duration_sec = call_duration_df['Agent_Call_Duration'].mean()

        td = timedelta(seconds=avg_call_duration_sec)
        # Extract hours, minutes, and seconds from the timedelta object
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        avg_call_duration_sec = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
         avg_call_duration_sec = '00:00:00'
    return avg_call_duration_sec

def avg_talk_time(talktime_df):
    if not talktime_df.empty:
        talktime_df = talktime_df[['agent_id','agent_name','Agent_Talk_Time']]
        avg_talk_time_sec = talktime_df['Agent_Talk_Time'].mean()

        td = timedelta(seconds=avg_talk_time_sec)
        # Extract hours, minutes, and seconds from the timedelta object
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        avg_talk_time_sec = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
         avg_talk_time_sec = '00:00:00'
    return avg_talk_time_sec

def avg_queue_time(queue_time_df):
    if not queue_time_df.empty:
        queue_time_df = queue_time_df[['agent_id','agent_name','Agent_Queue_Time']]
        avg_queue_time_sec = queue_time_df['Agent_Queue_Time'].mean()

        td = timedelta(seconds=avg_queue_time_sec)
        # Extract hours, minutes, and seconds from the timedelta object
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        avg_queue_time_sec = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
         avg_queue_time_sec = '00:00:00'

    return avg_queue_time_sec


def prod_hours(prod_df):
    if not prod_df.empty:
        prod_df = prod_df[['agent_id','agent_name','Productive_Hours']]
        pdf = prod_df.groupby(['agent_id','agent_name'])['Productive_Hours'].sum().reset_index(name='Productive_Hours')
    else:
        # Create an empty DataFrame with columns
        columns = ['agent_id', 'agent_name', 'campaign_id', 'campaign_name', 'wrapup_time', 'call_duration', 'wait_time', 'call_status_disposition', 'next_call_time', 'campaign_type', 'q_enter_time', 'q_leave_time', 'call_start_date_time', 'call_end_date_time']

        pdf = pd.DataFrame(columns=columns)
    return pdf

def unprod_hours(unprod_df):
    if not unprod_df.empty:
        unprod_df = unprod_df[['agent_id','agent_name','Unproductive_Hours']]
        updf = unprod_df.groupby(['agent_id','agent_name'])['Unproductive_Hours'].sum().reset_index(name='Unproductive_Hours')
    else:
        # Create an empty DataFrame with columns
        columns = ['agent_id', 'agent_name', 'campaign_id', 'campaign_name', 'wrapup_time', 'call_duration', 'wait_time', 'call_status_disposition', 'next_call_time', 'campaign_type', 'q_enter_time', 'q_leave_time', 'call_start_date_time', 'call_end_date_time']

        updf = pd.DataFrame(columns=columns)
    return updf

def wait_time(wait_time_df):
    if not wait_time_df.empty:
        waittime_df = wait_time_df[['agent_id','agent_name','Agent_Wait_Time','call_start_date_time']]
        wf = waittime_df.groupby(['agent_id','agent_name','call_start_date_time'])['Agent_Wait_Time'].sum().reset_index(name='Wait_Time')
    else:
        # Create an empty DataFrame with columns
        columns = ['agent_id', 'agent_name', 'campaign_id', 'campaign_name', 'wrapup_time', 'call_duration', 'wait_time', 'call_status_disposition', 'next_call_time', 'campaign_type', 'q_enter_time', 'q_leave_time', 'call_start_date_time', 'call_end_date_time']

        wf = pd.DataFrame(columns=columns)
    return wf

def wrapup_time(prod_df):
    if not prod_df.empty:
        wrapup_df = prod_df[['agent_id','agent_name','Agent_Wrapup_Time']]
        wf = wrapup_df.groupby(['agent_id','agent_name'])['Agent_Wrapup_Time'].sum().reset_index(name='Wrapup_Time')
    else:
        # Create an empty DataFrame with columns
        columns = ['agent_id', 'agent_name', 'campaign_id', 'campaign_name', 'wrapup_time', 'call_duration', 'wait_time', 'call_status_disposition', 'next_call_time', 'campaign_type', 'q_enter_time', 'q_leave_time', 'call_start_date_time', 'call_end_date_time']

        wf = pd.DataFrame(columns=columns)
    return wf

# call_duration  #kpi 6
def call_duration(prod_df):
    if not prod_df.empty:
        call_duration_df = prod_df[['agent_id','agent_name','Agent_Call_Duration']]
        cdf = call_duration_df.groupby(['agent_id','agent_name'])['Agent_Call_Duration'].sum().reset_index(name='Call_Duration')
    else:
        # Create an empty DataFrame with columns
        columns = ['agent_id', 'agent_name', 'campaign_id', 'campaign_name', 'wrapup_time', 'call_duration', 'wait_time', 'call_status_disposition', 'next_call_time', 'campaign_type', 'q_enter_time', 'q_leave_time', 'call_start_date_time', 'call_end_date_time']

        cdf = pd.DataFrame(columns=columns)
    return cdf

# talktime  #kpi 7
def talk_time(prod_df):
    if not prod_df.empty:
        talktime_df = prod_df[['agent_id','agent_name','Agent_Talk_Time']]
        ttdf = talktime_df.groupby(['agent_id','agent_name'])['Agent_Talk_Time'].sum().reset_index(name='Talk_Time')
    else:
        # Create an empty DataFrame with columns
        columns = ['agent_id', 'agent_name', 'campaign_id', 'campaign_name', 'wrapup_time', 'call_duration', 'wait_time', 'call_status_disposition', 'next_call_time', 'campaign_type', 'q_enter_time', 'q_leave_time', 'call_start_date_time', 'call_end_date_time']

        ttdf = pd.DataFrame(columns=columns)
    return ttdf


def queue_time(queue_time_df):
    if not queue_time_df.empty:
        queue_time_df = queue_time_df[['agent_id','agent_name','Agent_Queue_Time']]
        qtdf = queue_time_df.groupby(['agent_id','agent_name'])['Agent_Queue_Time'].sum().reset_index(name='Queue_Time')
    else:
        # Create an empty DataFrame with columns
        columns = ['agent_id', 'agent_name', 'campaign_id', 'campaign_name', 'wrapup_time', 'call_duration', 'wait_time', 'call_status_disposition', 'next_call_time', 'campaign_type', 'q_enter_time', 'q_leave_time', 'call_start_date_time', 'call_end_date_time']

        qtdf = pd.DataFrame(columns=columns)
    return qtdf


def agent_score(df):
     try:
        if not df.empty:
            a_date = df
            tmp_df = a_date.groupby(['agent_id','day_name'])['Score'].sum().reset_index()

            # Apply Min-Max normalization to the 'Score' column
            min_score = tmp_df['Score'].min()
            max_score = tmp_df['Score'].max()

            tmp_df['Normalized_Score'] = (tmp_df['Score'] - min_score) / (max_score - min_score) * 100

            # Getting top 10 rows based on "Normalized_Score"
            tmp_df = tmp_df.nlargest(10, 'Normalized_Score')
            # Rounding the "Normalized_Score" column to 3 decimal places
            tmp_df['Normalized_Score'] = tmp_df['Normalized_Score'].round(2)
        else:
             columns = ['agent_id','day_name','Agent_Average_Call_Duration','Agent_Average_Talk_Time','Agent_Average_Queue_Time','Agent_Average_Wait_Time','Agent_wrapup_time','Score','Normalized_Score']
             tmp_df = pd.DataFrame(columns=columns)
        return tmp_df
     except Exception as err:
          traceback.print_exc()
          log.error(str(err))

def agent_score_hourly(df):
     try:
        if not df.empty:
            a_date = df
            tmp_df = a_date.groupby(['hour'])['Score'].sum().reset_index()

            # Apply Min-Max normalization to the 'Score' column
            min_score = tmp_df['Score'].min()
            max_score = tmp_df['Score'].max()

            tmp_df['Normalized_Score'] = (tmp_df['Score'] - min_score) / (max_score - min_score) * 100

            # Rounding the "Normalized_Score" column to 3 decimal places
            tmp_df['Normalized_Score'] = tmp_df['Normalized_Score'].round(2)
        else:
             columns = ['agent_id','day_name','Agent_Average_Call_Duration','Agent_Average_Talk_Time','Agent_Average_Queue_Time','Agent_Average_Wait_Time','Agent_wrapup_time','Score','Normalized_Score','hour']
             tmp_df = pd.DataFrame(columns=columns)
        return tmp_df
     except Exception as err:
          traceback.print_exc()
          log.error(str(err))


def hourly_wrapup_call_duration_wait_time_hold_time(df):
    try:
        if not df.empty:
            # Calculate hourly trend analysis for the specified columns
            hourly_trends = df.groupby('hour').agg({
                'wrapup_time': 'mean',
                'call_duration': 'mean',
                'wait_time': 'mean',
                'hold_time': 'mean',
                'Agent_Talk_Time':'mean',
                'Agent_Queue_Time':'mean'
            }).reset_index()
        else:
            columns = ['wrapup_time','call_duration','wait_time','hold_time','Agent_Talk_Time','Agent_Queue_Time']
            hourly_trends = pd.DataFrame(columns=columns)
        return hourly_trends
    except Exception as err:
        traceback.print_exc()
        log.error(str(err))


def monthly_wrapup_call_duration_wait_time_hold_time(df):
    try:
        if not df.empty:
            # Calculate monthly trend analysis for the specified columns
            monthly_trends = df.groupby('months').agg({
                'wrapup_time': 'mean',
                'call_duration': 'mean',
                'wait_time': 'mean',
                'hold_time': 'mean',
                'Agent_Talk_Time':'mean',
                'Agent_Queue_Time':'mean'
            }).reset_index()
        else:
            columns = ['wrapup_time','call_duration','wait_time','hold_time','Agent_Talk_Time','Agent_Queue_Time']
            monthly_trends = pd.DataFrame(columns=columns)
        return monthly_trends
    except Exception as err:
        traceback.print_exc()
        log.error(str(err))


def days_wrapup_call_duration_wait_time_hold_time(df):
    try:
        if not df.empty:
            # Calculate monthly trend analysis for the specified columns
            days_trends = df.groupby('days').agg({
                'wrapup_time': 'mean',
                'call_duration': 'mean',
                'wait_time': 'mean',
                'hold_time': 'mean',
                'Agent_Talk_Time':'mean',
                'Agent_Queue_Time':'mean'
            }).reset_index()
        else:
            columns = ['wrapup_time','call_duration','wait_time','hold_time','Agent_Talk_Time','Agent_Queue_Time']
            days_trends = pd.DataFrame(columns=columns)
        return days_trends
    except Exception as err:
        traceback.print_exc()
        log.error(str(err))


def main_test(selected_campaign_name,start_date,end_date):
    today_date = get_date()

    df = read_csv_files(selected_campaign_name,start_date,end_date,today_date)
    df1 = read_csv_files_current_report(selected_campaign_name,start_date,end_date,today_date)
    
    avg_productive_hour = avg_prod_hours(df)
    avg_unproductive_hour = avg_unprod_hours(df)
    avg_wait_time_sec = avg_wait_time(df)
    avg_wrapup_time_sec = avg_wrapup_time(df)
    avg_call_duration_sec = avg_call_duration(df)
    avg_talk_time_sec = avg_talk_time(df)
    avg_queue_time_sec = avg_queue_time(df)
    avg_score = eda_call_status(df1)

    productive_df = prod_hours(df)
    if not  productive_df.empty:
        productive_df = productive_df.to_dict(orient="records")
    else:
        productive_df = [{'agent_id': 0, 'agent_name': 'Nishant Saxena', 'Productive_Hours': '0 days 00:00:00'}]

    unproductive_df = unprod_hours(df)
    if not unproductive_df.empty:
        unproductive_df = unproductive_df.to_dict(orient="records")
    else:
        unproductive_df = [{'agent_id': 0, 'agent_name': 'Nishant Saxena', 'Unproductive_Hours': '0 days 00:00:00'}]

    wait_time_df = wait_time(df)
    if not wait_time_df.empty:
        wait_time_df = wait_time_df.to_dict(orient="records")
    else:
        wait_time_df = [{'agent_id': 0, 'agent_name': 'Nishant Saxena', 'call_start_date_time': '0000-00-00 00:00:00', 'Wait_Time': 0}]

    wrapup_time_df = wrapup_time(df)
    if not wrapup_time_df.empty:
        wrapup_time_df = wrapup_time_df.to_dict(orient="records")
    else:
        wrapup_time_df = [{'agent_id': 0, 'agent_name': 'Nishant Saxena', 'Wrapup_Time': 0}]

    call_duration_df = call_duration(df)
    if not call_duration_df.empty:
        call_duration_df = call_duration_df.to_dict(orient="records")
    else:
        call_duration_df = [{'agent_id': 0, 'agent_name': 'Nishant Saxena', 'Call_Duration': 0}]

    talk_time_df = talk_time(df)
    if not talk_time_df.empty:
        talk_time_df = talk_time_df.to_dict(orient="records")
    else:
        talk_time_df = [{'agent_id': 0, 'agent_name': 'Nishant Saxena', 'Talk_Time': 0}]

    queue_time_df = queue_time(df)
    if not queue_time_df.empty:
        queue_time_df = queue_time_df.to_dict(orient="records")
    else:
        queue_time_df = [{'agent_id': 0, 'agent_name': 'Nishant Saxena', 'Queue_Time': 0}]

    agent_score_df = agent_score(df1)
    if not agent_score_df.empty:
        agent_score_df = agent_score_df.to_dict(orient="records")
    else:
        agent_score_df = [{'agent_id': 0, 'day_name': '0', 'Score': 0, 'Normalized_Score': 0}]

    agent_score_hourly_df = agent_score_hourly(df1)
    if not agent_score_hourly_df.empty:
        agent_score_hourly_df = agent_score_hourly_df.to_dict(orient="records")
    else:
        agent_score_hourly_df = [{'hour': 9, 'Score': 0, 'Normalized_Score': 0}]

    hourly_trends_df = hourly_wrapup_call_duration_wait_time_hold_time(df1)
    if not hourly_trends_df.empty:
        hourly_trends_df = hourly_trends_df.to_dict(orient="records")
    else:
        hourly_trends_df = [{'hour': 9, 'wrapup_time': 0, 'call_duration': 0, 'wait_time': 0, 'hold_time': 0, 'Agent_Talk_Time': 0, 'Agent_Queue_Time': 0}]

    month_trends_df = monthly_wrapup_call_duration_wait_time_hold_time(df1)
    if not month_trends_df.empty:
        month_trends_df = month_trends_df.to_dict(orient="records")
    else:
        month_trends_df = [{'months': 7, 'wrapup_time': 0, 'call_duration': 0, 'wait_time': 0, 'hold_time': 0, 'Agent_Talk_Time': 0, 'Agent_Queue_Time': 0}]

    days_trends_df = days_wrapup_call_duration_wait_time_hold_time(df1)
    if not days_trends_df.empty:
        days_trends_df = days_trends_df.to_dict(orient="records")
    else:
        days_trends_df = [{'days': 15, 'wrapup_time':0, 'call_duration': 0, 'wait_time': 0, 'hold_time': 0, 'Agent_Talk_Time': 0, 'Agent_Queue_Time': 0}]

    return [avg_productive_hour,avg_unproductive_hour,avg_wait_time_sec,avg_wrapup_time_sec,avg_call_duration_sec,avg_talk_time_sec,avg_queue_time_sec,avg_score,productive_df,unproductive_df,wait_time_df,wrapup_time_df,call_duration_df,talk_time_df,queue_time_df,agent_score_df,agent_score_hourly_df,hourly_trends_df,month_trends_df,days_trends_df]
