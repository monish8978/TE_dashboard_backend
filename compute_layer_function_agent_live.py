"""
import settings file
"""
from settings import common_csv_file_path_agent,compute_layer_log_path,download_csv_row_data_agent_csv_path,live_day_count,download_csv_row_data_agent
"""
        import modules
"""
from datetime import datetime,timedelta
import pandas as pd
import traceback
import threading
import logging
import warnings
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

def get_date():
        try:
                today = datetime.now()
                yesterday = today - timedelta(days=live_day_count)
                yesterday_date = yesterday.strftime('%Y-%m-%d')
                return yesterday_date
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def reading_agent_csv(yesterday_date):
    try:
        # agent state analysis csv file
        file_name = f'{common_csv_file_path_agent}agent_state_analysis_{yesterday_date}.csv'
        if os.path.exists(file_name):
            agent_df = pd.read_csv(file_name)
            agent_df = agent_df.dropna(axis=1,how='all')
                        # rename columns and set new columns
            agent_df.rename(columns=lambda x : x.replace(' ','_').lower(),inplace = True)
            # making new columns by converting the datatype of column to datetime.
            agent_df['day_name'] = pd.to_datetime(agent_df['call_start_date_time']).dt.strftime('%d %B')
            agent_df['month_name'] = pd.to_datetime(agent_df['call_start_date_time']).dt.month_name()
            agent_df['start_time'] = pd.to_datetime(agent_df['call_start_date_time'], errors='coerce')
            agent_df['end_time'] = pd.to_datetime(agent_df['call_end_date_time'],errors='coerce')
            agent_df['date_time_temp'] = agent_df['start_time'].dt.strftime('%Y-%m-%d 00:00:00')
            # print(agent_df,"------------")
            if 'break_type' not in agent_df.columns:
                agent_df['break_type'] = None  # or '' depending on your preference
            # Clean the dataset
            agent_df = agent_df[['agent_id', 'agent_name', 'call_start_date_time', 'call_end_date_time','agent_state','break_type','day_name','month_name','date_time_temp']]
            return agent_df
        else:
            err = "Data Not Found!"
            log.error(str(err))
    except Exception as err:
         log.error(str(err))
         traceback.print_exc()


def reading_detailed_call_report_csv(yesterday_date):
    try:
        tmp_df_list = []
        items = os.listdir(download_csv_row_data_agent)
        # Case-insensitive sorting
        items = sorted(items, key=str.lower)
        for campaign_name in items:
            if campaign_name != "campaignname":
                directory_path = f"{download_csv_row_data_agent}{campaign_name}/"
                file_name = f'{directory_path}{yesterday_date}.csv'

                if os.path.exists(file_name):
                    dc_df = pd.read_csv(file_name)
                    dc_df.rename(columns=lambda x: x.replace(' ', '_').lower(), inplace=True)

                    # adding new column 'date' and 'month' in dataset.
                    dc_df['date_time'] = pd.to_datetime(dc_df['call_start_date_time'])
                    dc_df['day_name'] = dc_df['date_time'].dt.strftime('%d %B')
                    dc_df['month_name'] = dc_df['date_time'].dt.month_name()

                    #----------------------------ringtime calculations-----------------#
                    dc_df['ringstart_time'] = pd.to_datetime(dc_df['ringstart_time'], errors='coerce')
                    dc_df['ringend_time'] = pd.to_datetime(dc_df['ringend_time'], errors='coerce')
                    dc_df['ring_duration(sec)'] = (dc_df['ringend_time'] - dc_df['ringstart_time']).dt.total_seconds()
                    dc_df['ring_duration(sec)'] = dc_df['ring_duration(sec)'].fillna(0)

                    #----------------------queue time calculations-----------#
                    dc_df['q_leave_time'] = pd.to_datetime(dc_df['q_leave_time'], errors='coerce')
                    dc_df['q_enter_time'] = pd.to_datetime(dc_df['q_enter_time'], errors='coerce')
                    dc_df['queue_time(sec)'] = (dc_df['q_leave_time']- dc_df['q_enter_time']).dt.total_seconds()

                    #---------actual talktime calculations---------------#
                    dc_df['actual_talktime(sec)'] = dc_df['call_duration'] -  dc_df['ring_duration(sec)'] - dc_df['hold_time']

                    #------------agent call duration------------#
                    dc_df['agent_call_duration(sec)'] = dc_df['ring_duration(sec)'] + dc_df['call_duration']

                    agent_id = set(dc_df['agent_id'])

                    productive_call_status = ['answered', 'transfer']
                    dc_df = dc_df.loc[(dc_df['campaign_type'].isin(['OUTBOUND', 'INBOUND'])) & (dc_df['call_status_disposition'].isin(productive_call_status))]
                    tmp_df_list.append(dc_df)
        return tmp_df_list,items
    except Exception as err:
         log.error(str(err))
         traceback.print_exc()


def overall_df(tmp_df_list,agent_csv,items,yesterday_date):
    try:
        for df_act,campaign_tmp in zip(tmp_df_list,items):
            if not df_act.empty:
                working_agents = agent_csv # agent wise information csv
                # Agent Average call_duration/Day
                average_call_duration_df = df_act[['agent_id','agent_call_duration(sec)','day_name','month_name']]
                average_call_d_day = average_call_duration_df.groupby(['agent_id','day_name'])['agent_call_duration(sec)'].sum().reset_index(name='Agent_Call_Duration')

                # Agent Average talk time/Day
                average_talk_time_df = df_act[['agent_id','actual_talktime(sec)','day_name','month_name']]
                average_tt_day = average_talk_time_df.groupby(['agent_id','day_name'])['actual_talktime(sec)'].sum().reset_index(name='Agent_Talk_Time')

                # # average queue time/agent => day wise
                average_queue_time_df = df_act[['agent_id','queue_time(sec)','day_name','month_name']]
                average_queue_time_day = average_queue_time_df.groupby(['agent_id','day_name'])['queue_time(sec)'].sum().reset_index(name='Agent_Queue_Time')

                # # Agent Average wait time/Day
                average_wait_time_df = df_act[['agent_id','wait_time','day_name','month_name']]
                average_wt_day = average_wait_time_df.groupby(['agent_id','day_name'])['wait_time'].sum().reset_index(name='Agent_Wait_Time')

                # Agent Average wrapup_time/Day
                average_wrapup_time_df = df_act[['agent_id','wrapup_time','day_name','month_name']]
                average_wpt_day = average_wrapup_time_df.groupby(['agent_id','day_name'])['wrapup_time'].sum().reset_index(name='Agent_Wrapup_Time')

                # combined day
                a_date = pd.merge(average_call_d_day,average_tt_day,on=['agent_id','day_name'])
                a_date = pd.merge(a_date,average_queue_time_day,on=['agent_id','day_name'])
                a_date = pd.merge(a_date,average_wt_day,on=['agent_id','day_name'])
                a_date = pd.merge(a_date,average_wpt_day,on=['agent_id','day_name'])

                # Identify invalid datetime strings
                invalid_datetime = '0000-00-00 00:00:00'

                # Replace invalid datetime strings with NaT (Not a Time)
                working_agents['call_end_date_time'] = working_agents['call_end_date_time'].replace(invalid_datetime, pd.NaT)

                # #----------------agent computation---------------#
                # # Convert the columns to datetime
                working_agents['call_start_date_time'] = pd.to_datetime(working_agents['call_start_date_time'])
                working_agents['call_end_date_time'] = pd.to_datetime(working_agents['call_end_date_time'])

                lists = ['Tea','Lunch','Lunchbreak','Teabreak','Meal','Snacks','Washroom','Others','BREAK']
                #------------------------filter the data based upon some criteria------------------------------------#
                agent_data = working_agents.loc[(working_agents['agent_state'] == 'LOGIN_N_LOGOUT')]
                break_data = working_agents.loc[(working_agents['agent_state'] == 'BREAK_N_BACK') & (working_agents['break_type'].isin(lists))]

                #------------------Grouping and perform date wise analysis for every agent-------------------------#
                # agent data#
                agent_data['total_time(seconds)'] = (agent_data.call_end_date_time - agent_data.call_start_date_time)

                # filtered_agent_data_date = agent_data.groupby(['agent_id','agent_name','day_name','month_name','date_time_temp'])['total_time(seconds)'].sum().reset_index(name='Total_Login_Time')

                # Group by 'minutes' and sum 'total_time(seconds)'
                filtered_agent_data_date = agent_data.groupby(['agent_id','agent_name','day_name','month_name','date_time_temp']).agg({'call_start_date_time': 'first', 'total_time(seconds)': 'sum'})

                filtered_agent_data_date = filtered_agent_data_date.reset_index()

                # Renaming columns
                filtered_agent_data_date = filtered_agent_data_date.rename(columns={'total_time(seconds)': 'Total_Login_Time'})
                # print(filtered_agent_data_date)

                # break data#
                break_data['total_time(seconds)'] = (break_data.call_end_date_time - break_data.call_start_date_time)

                # Group by 'minutes' and sum 'total_time(seconds)'
                filtered_break_data_date = break_data.groupby(['agent_id','agent_name','day_name','month_name','date_time_temp']).agg({'call_start_date_time': 'first', 'total_time(seconds)': 'sum'})

                filtered_break_data_date = filtered_break_data_date.reset_index()

                # Renaming columns
                filtered_break_data_date = filtered_break_data_date.rename(columns={'total_time(seconds)': 'Unproductive_Hours'})

                # filtered_break_data_date = break_data.groupby(['agent_id','agent_name','day_name','month_name','date_time_temp'])['total_time(seconds)'].sum().reset_index(name='Unproductive_Hours')

                # FILTERED DATAFRAME
                new_dataframe_date = filtered_agent_data_date.merge(filtered_break_data_date,on=['agent_id','agent_name','day_name','month_name','date_time_temp','call_start_date_time'],how='left')

                new_dataframe_date.fillna('0 days 00:00:00',inplace=True)
                new_dataframe_date['Productive_Hours'] = new_dataframe_date['Total_Login_Time'] - new_dataframe_date['Unproductive_Hours']

                def update_time(time):
                    if time >= pd.to_timedelta('0 days 12:00:00'):
                        return pd.to_timedelta('0 days 08:00:00')
                    else:
                        return time

                new_dataframe_date['Productive_Hours'] = new_dataframe_date['Productive_Hours'].apply(update_time)

                new_date_df = a_date.merge(new_dataframe_date,on=['agent_id','day_name'],how='left')
                new_date_df.dropna(subset=['Total_Login_Time'],inplace=True)

                file_name = yesterday_date+".csv"
                dc_path = f'{download_csv_row_data_agent_csv_path}{campaign_tmp}/'

                if not os.path.exists(dc_path):
                    os.makedirs(dc_path)
                new_date_df.to_csv(dc_path+file_name,index=False)
    except Exception as err:
        log.info(str(err))
        traceback.print_exc()


def delete_csv_file(yesterday_date):
    try:
        # file name
        agent_file_name = f'{common_csv_file_path_agent}agent_state_analysis_{yesterday_date}.csv'
        deatil_report_file_name = f'{common_csv_file_path_agent}detailed_call_report_{yesterday_date}.csv'

        if os.path.exists(agent_file_name):
            os.remove(agent_file_name)

        if os.path.exists(deatil_report_file_name):
            os.remove(deatil_report_file_name)
    except Exception as err:
        log.error(str(err))
        traceback.print_exc()


def main():
    yesterday_date = get_date()
    dc_df,items = reading_detailed_call_report_csv(yesterday_date)
    agent_csv = reading_agent_csv(yesterday_date)
    overall_df(dc_df,agent_csv,items,yesterday_date)
    delete_csv_file(yesterday_date)
