from settings import (
    common_csv_file_path_agent,
    compute_layer_log_path,
    download_csv_row_data_agent_csv_path,
    day_count,
    download_csv_row_data_agent
)

from datetime import datetime, timedelta
import pandas as pd
import traceback
import threading
import logging
import warnings
import os

warnings.filterwarnings("ignore")

# ---------------- LOGGING ---------------- #
logname = compute_layer_log_path
logging.basicConfig(filename=logname, level=logging.DEBUG)
log = logging.getLogger()
fh = logging.FileHandler(logname, mode='a+')

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(funcName)s %(levelname)s - %(lineno)d - %(message)s"
)
fh.setFormatter(formatter)
log.addHandler(fh)

log.info("Loading....")

lock = threading.Lock()


# ---------------- DATE ---------------- #
def get_date():
    try:
        today = datetime.now()
        yesterday = today - timedelta(days=day_count)
        return yesterday.strftime('%Y-%m-%d')
    except Exception as err:
        log.error(str(err))
        traceback.print_exc()


# ---------------- READ AGENT CSV ---------------- #
def reading_agent_csv(yesterday_date):
    try:
        file_name = f'{common_csv_file_path_agent}agent_state_analysis_{yesterday_date}.csv'

        if not os.path.exists(file_name):
            log.error("Agent CSV not found")
            return None

        agent_df = pd.read_csv(file_name)
        agent_df = agent_df.dropna(axis=1, how='all')

        agent_df.rename(columns=lambda x: x.replace(' ', '_').lower(), inplace=True)

        required_cols = [
            'agent_id', 'agent_name',
            'call_start_date_time', 'call_end_date_time',
            'agent_state'
        ]

        for col in required_cols:
            if col not in agent_df.columns:
                log.error(f"Missing required column: {col}")
                return None

        if 'break_type' not in agent_df.columns:
            agent_df['break_type'] = None

        agent_df['call_start_date_time'] = pd.to_datetime(agent_df['call_start_date_time'], errors='coerce')
        agent_df['call_end_date_time'] = pd.to_datetime(agent_df['call_end_date_time'], errors='coerce')

        agent_df['day_name'] = agent_df['call_start_date_time'].dt.strftime('%d %B')
        agent_df['month_name'] = agent_df['call_start_date_time'].dt.month_name()
        agent_df['date_time_temp'] = agent_df['call_start_date_time'].dt.strftime('%Y-%m-%d 00:00:00')

        return agent_df

    except Exception as err:
        log.error(str(err))
        traceback.print_exc()
        return None


# ---------------- CALL REPORT ---------------- #
def reading_detailed_call_report_csv(yesterday_date):
    try:
        tmp_df_list = []
        items = sorted(os.listdir(download_csv_row_data_agent), key=str.lower)

        for campaign_name in items:
            if campaign_name == "campaignname":
                continue

            file_name = f"{download_csv_row_data_agent}{campaign_name}/{yesterday_date}.csv"

            if not os.path.exists(file_name):
                continue

            dc_df = pd.read_csv(file_name)
            dc_df.rename(columns=lambda x: x.replace(' ', '_').lower(), inplace=True)

            dc_df['date_time'] = pd.to_datetime(dc_df['call_start_date_time'], errors='coerce')
            dc_df['day_name'] = dc_df['date_time'].dt.strftime('%d %B')
            dc_df['month_name'] = dc_df['date_time'].dt.month_name()

            dc_df['ringstart_time'] = pd.to_datetime(dc_df['ringstart_time'], errors='coerce')
            dc_df['ringend_time'] = pd.to_datetime(dc_df['ringend_time'], errors='coerce')
            dc_df['ring_duration(sec)'] = (dc_df['ringend_time'] - dc_df['ringstart_time']).dt.total_seconds().fillna(0)

            dc_df['q_enter_time'] = pd.to_datetime(dc_df['q_enter_time'], errors='coerce')
            dc_df['q_leave_time'] = pd.to_datetime(dc_df['q_leave_time'], errors='coerce')
            dc_df['queue_time(sec)'] = (dc_df['q_leave_time'] - dc_df['q_enter_time']).dt.total_seconds()

            dc_df['actual_talktime(sec)'] = (
                dc_df['call_duration'] - dc_df['ring_duration(sec)'] - dc_df['hold_time']
            )

            dc_df['agent_call_duration(sec)'] = (
                dc_df['ring_duration(sec)'] + dc_df['call_duration']
            )

            dc_df = dc_df[
                (dc_df['campaign_type'].isin(['OUTBOUND', 'INBOUND'])) &
                (dc_df['call_status_disposition'].isin(['answered', 'transfer']))
            ]

            if not dc_df.empty:
                tmp_df_list.append(dc_df)

        return tmp_df_list, items

    except Exception as err:
        log.error(str(err))
        traceback.print_exc()
        return [], []


# ---------------- MAIN PROCESS ---------------- #
def overall_df(tmp_df_list, agent_csv, items, yesterday_date):
    try:
        if agent_csv is None or agent_csv.empty:
            log.error("Agent CSV empty")
            return

        for df_act, campaign_tmp in zip(tmp_df_list, items):

            if df_act.empty:
                continue

            working_agents = agent_csv.copy()

            working_agents['break_type'] = working_agents['break_type'].astype(str).str.lower()

            # ---------------- KPI GROUP ---------------- #
            a_date = df_act.groupby(['agent_id', 'day_name']).agg({
                'agent_call_duration(sec)': 'sum',
                'actual_talktime(sec)': 'sum',
                'queue_time(sec)': 'sum',
                'wait_time': 'sum',
                'wrapup_time': 'sum'
            }).reset_index()

            a_date.rename(columns={
                'agent_call_duration(sec)': 'Agent_Call_Duration',
                'actual_talktime(sec)': 'Agent_Talk_Time',
                'queue_time(sec)': 'Agent_Queue_Time',
                'wait_time': 'Agent_Wait_Time',
                'wrapup_time': 'Agent_Wrapup_Time'
            }, inplace=True)

            # 🔥 ADD call_start_date_time (FIX REQUEST)
            base_time = df_act[['agent_id', 'day_name', 'call_start_date_time']].copy()
            a_date = a_date.merge(base_time, on=['agent_id', 'day_name'], how='left')

            # ---------------- LOGIN / BREAK ---------------- #
            lists = ['tea','lunch','lunchbreak','teabreak','meal','snacks','washroom','others','break']

            agent_data = working_agents[working_agents['agent_state'] == 'LOGIN_N_LOGOUT']
            break_data = working_agents[
                (working_agents['agent_state'] == 'BREAK_N_BACK') &
                (working_agents['break_type'].isin(lists))
            ]

            if agent_data.empty:
                log.warning("No login data")
                continue

            agent_data['total_time'] = (
                agent_data['call_end_date_time'] - agent_data['call_start_date_time']
            )

            login_df = agent_data.groupby(
                ['agent_id', 'agent_name', 'day_name']
            )['total_time'].sum().reset_index(name='Total_Login_Time')

            if break_data.empty:
                break_df = pd.DataFrame(columns=[
                    'agent_id', 'agent_name', 'day_name', 'Unproductive_Hours'
                ])
            else:
                break_data['total_time'] = (
                    break_data['call_end_date_time'] - break_data['call_start_date_time']
                )

                break_df = break_data.groupby(
                    ['agent_id', 'agent_name', 'day_name']
                )['total_time'].sum().reset_index(name='Unproductive_Hours')

            final_df = login_df.merge(break_df, on=['agent_id','agent_name','day_name'], how='left')
            final_df['Unproductive_Hours'] = final_df['Unproductive_Hours'].fillna(pd.Timedelta(0))

            final_df['Productive_Hours'] = (
                final_df['Total_Login_Time'] - final_df['Unproductive_Hours']
            )

            final_df['Productive_Hours'] = final_df['Productive_Hours'].apply(
                lambda x: pd.Timedelta(hours=8) if x >= pd.Timedelta(hours=12) else x
            )

            # ---------------- FINAL MERGE ---------------- #
            new_date_df = a_date.merge(final_df, on=['agent_id','day_name'], how='left')

            # save
            dc_path = f'{download_csv_row_data_agent_csv_path}{campaign_tmp}/'
            os.makedirs(dc_path, exist_ok=True)

            file_name = f"{yesterday_date}.csv"
            new_date_df.to_csv(dc_path + file_name, index=False)

            #print("Saved:", file_name)

    except Exception as err:
        log.error(str(err))
        traceback.print_exc()


# ---------------- DELETE FILES ---------------- #
def delete_csv_file(yesterday_date):
    try:
        files = [
            f'{common_csv_file_path_agent}agent_state_analysis_{yesterday_date}.csv',
            f'{common_csv_file_path_agent}detailed_call_report_{yesterday_date}.csv'
        ]

        for f in files:
            if os.path.exists(f):
                os.remove(f)

    except Exception as err:
        log.error(str(err))
        traceback.print_exc()


# ---------------- MAIN ---------------- #
def main():
    yesterday_date = get_date()

    dc_df, items = reading_detailed_call_report_csv(yesterday_date)
    agent_csv = reading_agent_csv(yesterday_date)

    if agent_csv is None:
        log.error("Agent CSV missing")
        return

    overall_df(dc_df, agent_csv, items, yesterday_date)
    delete_csv_file(yesterday_date)


if __name__ == "__main__":
    main()
