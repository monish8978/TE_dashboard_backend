"""
        import settings file
"""
from settings import campaign_detailed_call_report_csv_file_path,compute_layer_function_log_path
"""
        import modules
"""
import os
import pandas as pd
from datetime import datetime,timedelta
import traceback
import fnmatch
import logging
import threading

logname = compute_layer_function_log_path
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

def read_csv_files(selected_campaign_name,start_date,end_date,selected_campaign_type):
    try:
            # Use datetime.combine to convert date to datetime
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.min.time())

            # csv_file_path
            folder_path = f"{campaign_detailed_call_report_csv_file_path}{selected_campaign_name}/"

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
            if selected_campaign_type == "ALL":
                    combined_df = combined_df
            elif selected_campaign_type == "INBOUND" or selected_campaign_type == "OUTBOUND":
                    try:
                            combined_df = combined_df[combined_df['campaign_type'] == selected_campaign_type]
                    except:
                            combined_df = combined_df
            if combined_df.empty:
                            # Create an empty DataFrame with columns
                            columns = ['date','campaign_name','operator','circle','call_status_disposition','datetime_combined','hour','time']
                            combined_df = pd.DataFrame(columns=columns)

            return combined_df
    except Exception as err:
            log.error(str(err))
            traceback.print_exc()


def total_call_count_data_set(df):
        try:
                if not df.empty:
                        overall_wise_call = df.groupby(['campaign_name'])["campaign_name"].size().reset_index(name='count')
                else:
                        # Create an empty DataFrame with columns
                        overall_wise_call = ['campaign_name', 'count']
                        overall_wise_call = pd.DataFrame(columns=overall_wise_call)
                return overall_wise_call
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()


def total_inbound_outbound_call_data_set(df):
        try:
                if not df.empty:
                        inbound_outbound_df = df.groupby(['campaign_type'])["campaign_type"].size().reset_index(name='count')
                else:
                        # Create an empty DataFrame with columns
                        inbound_outbound_df = ['campaign_type', 'count']
                        inbound_outbound_df = pd.DataFrame(columns=inbound_outbound_df)
                inbound_df = inbound_outbound_df[inbound_outbound_df['campaign_type'] == 'INBOUND']
                outbound_df = inbound_outbound_df[inbound_outbound_df['campaign_type'] == 'OUTBOUND']
                return inbound_df,outbound_df
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()


def total_dialer_type_df_call_data_set(df):
        try:
                if not df.empty:
                        dialer_type_df = df.groupby(['dialer_type'])['dialer_type'].size().reset_index(name='count')
                else:
                        # Create an empty DataFrame with columns
                        dialer_type_df = ['dialer_type', 'count']
                        dialer_type_df = pd.DataFrame(columns=dialer_type_df)
                auto_dial_df = dialer_type_df[dialer_type_df['dialer_type'] == 'AUTODIAL']
                preview_df = dialer_type_df[dialer_type_df['dialer_type'] == 'PREVIEW']
                progressive_df = dialer_type_df[dialer_type_df['dialer_type'] == 'PROGRESSIVE']
                return auto_dial_df,preview_df,progressive_df
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()


def region_data_set(df):
        try:
                if not df.empty:
                        region_call = df.groupby(['circle'])['circle'].size().reset_index(name='count')
                else:
                        # Create an empty DataFrame with columns
                        region_call = ['circle', 'count']
                        region_call = pd.DataFrame(columns=region_call)
                return region_call
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def success_failure_region_wise_data_set(df):
        try:
                if not df.empty:
                        df = df[['call_status_disposition','call_duration','circle','hour','datetime_combined']]
                else:
                        # Create an empty DataFrame with columns
                        df = ['call_status_disposition','call_duration','circle','hour','datetime_combined']
                        df = pd.DataFrame(columns=df)

                return df
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def operator_region_wise_data_set(df):
        try:
                if not df.empty:
                        df = df[['circle','operator']]
                else:
                        # Create an empty DataFrame with columns
                        df = ['circle','operator']
                        df = pd.DataFrame(columns=df)

                return df
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def operator_data_set(df):
        try:
                if not df.empty:
                        operator_call = df.groupby(['operator'])['operator'].size().reset_index(name='count')
                else:
                        # Create an empty DataFrame with columns
                        operator_call = ['circle','operator']
                        operator_call = pd.DataFrame(columns=operator_call)
                return operator_call
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def success_failure_operator_wise_data_set(df):
        try:
                if not df.empty:
                        df = df[['call_status_disposition','call_duration','operator','hour']]
                else:
                        # Create an empty DataFrame with columns
                        df = ['call_status_disposition','call_duration','operator','hour']
                        df = pd.DataFrame(columns=df)
                return df
        except Exception as err:
                traceback.print_exc()

def call_status_dis_operator_wise_data_set(df):
        try:
                if not df.empty:
                        df = df[['call_status_disposition','operator']]
                else:
                        # Create an empty DataFrame with columns
                        df = ['call_status_disposition','operator']
                        df = pd.DataFrame(columns=df)
                return df
        except Exception as err:
                traceback.print_exc()

def over_all_call_status_dis_data_set(df):
        try:
                if not df.empty:
                        over_all_call_status_dis = df.groupby(['call_status_disposition'])['call_status_disposition'].size().reset_index(name='count')
                else:
                        # Create an empty DataFrame with columns
                        over_all_call_status_dis = ['call_status_disposition','count']
                        over_all_call_status_dis = pd.DataFrame(columns=over_all_call_status_dis)
                return over_all_call_status_dis
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()


def operator_call_count_hour_data_set(df):
        try:
                df = df.groupby(['campaign_name','hour','date','datetime_combined','operator'])['time'].size().reset_index(name='count')
                # Assuming your DataFrame is named df
                df['hour'] = df['hour'].apply(lambda x: f'{x:02}')
                df = df.groupby(['hour','operator'])['count'].sum().reset_index(name='count')

                hour_list = []
                for tmp_hour in range(0,24):
                        # Check if the integer has a single digit
                        if isinstance(tmp_hour, int) and len(str(tmp_hour)) == 1:
                                tmp_hour = "0"+str(tmp_hour)
                                hour_list.append(tmp_hour)
                        else:
                                tmp_hour = str(tmp_hour)
                                hour_list.append(tmp_hour)

                # Convert DataFrame to the specified format
                formatted_data = {}
                for _, row in df.iterrows():
                        hour = str(row['hour'])
                        operator = row['operator']
                        count_value = row['count']

                        if hour not in formatted_data:
                                formatted_data[hour] = {}

                        formatted_data[hour][operator] = {'count value': count_value}

                Airtel_update_op_dict= {}
                Others_update_op_dict = {}
                Reliance_update_op_dict = {}
                BSNL_MTNL_update_op_dict = {}
                Vodafone_Idea_update_op_dict = {}

                for hr in hour_list:
                        if hr in formatted_data.keys():
                                if 'Airtel' in formatted_data[hr].keys():
                                        tmp_dict = formatted_data[hr]['Airtel']
                                        Airtel_tmp_value = tmp_dict['count value']
                                        Airtel_cnt_dict = {hr:Airtel_tmp_value}
                                        Airtel_update_op_dict.update(Airtel_cnt_dict)
                                else:
                                        Airtel_tmp_value = 0
                                        Airtel_cnt_dict = {hr:Airtel_tmp_value}
                                        Airtel_update_op_dict.update(Airtel_cnt_dict)

                                if 'Others' in formatted_data[hr].keys():
                                        tmp_dict = formatted_data[hr]['Others']
                                        Others_tmp_value = tmp_dict['count value']
                                        Others_cnt_dict = {hr:Others_tmp_value}
                                        Others_update_op_dict.update(Others_cnt_dict)
                                else:
                                        Others_tmp_value = 0
                                        Others_cnt_dict = {hr:Others_tmp_value}
                                        Others_update_op_dict.update(Others_cnt_dict)

                                if 'Reliance Jio' in formatted_data[hr].keys():
                                        tmp_dict = formatted_data[hr]['Reliance Jio']
                                        Reliance_tmp_value = tmp_dict['count value']
                                        Reliance_cnt_dict = {hr:Reliance_tmp_value}
                                        Reliance_update_op_dict.update(Reliance_cnt_dict)
                                else:
                                        Reliance_tmp_value = 0
                                        Reliance_cnt_dict = {hr:Reliance_tmp_value}
                                        Reliance_update_op_dict.update(Reliance_cnt_dict)

                                if 'BSNL/MTNL' in formatted_data[hr].keys():
                                        tmp_dict = formatted_data[hr]['BSNL/MTNL']
                                        BSNL_MTNL_tmp_value = tmp_dict['count value']
                                        BSNL_MTNL_cnt_dict = {hr:BSNL_MTNL_tmp_value}
                                        BSNL_MTNL_update_op_dict.update(BSNL_MTNL_cnt_dict)
                                else:
                                        BSNL_MTNL_tmp_value = 0
                                        BSNL_MTNL_cnt_dict = {hr:BSNL_MTNL_tmp_value}
                                        BSNL_MTNL_update_op_dict.update(BSNL_MTNL_cnt_dict)

                                if 'Vodafone Idea' in formatted_data[hr].keys():
                                        tmp_dict = formatted_data[hr]['Vodafone Idea']
                                        Vodafone_Idea_tmp_value = tmp_dict['count value']
                                        Vodafone_Idea_cnt_dict = {hr:Vodafone_Idea_tmp_value}
                                        Vodafone_Idea_update_op_dict.update(Vodafone_Idea_cnt_dict)
                                else:
                                        Vodafone_Idea_tmp_value = 0
                                        Vodafone_Idea_cnt_dict = {hr:Vodafone_Idea_tmp_value}
                                        Vodafone_Idea_update_op_dict.update(Vodafone_Idea_cnt_dict)

                        else:
                                Airtel_tmp_value = 0
                                Airtel_cnt_dict = {hr:Airtel_tmp_value}
                                Airtel_update_op_dict.update(Airtel_cnt_dict)

                                Others_tmp_value = 0
                                Others_cnt_dict = {hr:Others_tmp_value}
                                Others_update_op_dict.update(Others_cnt_dict)

                                Reliance_tmp_value = 0
                                Reliance_cnt_dict = {hr:Reliance_tmp_value}
                                Reliance_update_op_dict.update(Reliance_cnt_dict)

                                BSNL_MTNL_tmp_value = 0
                                BSNL_MTNL_cnt_dict = {hr:BSNL_MTNL_tmp_value}
                                BSNL_MTNL_update_op_dict.update(BSNL_MTNL_cnt_dict)

                                Vodafone_Idea_tmp_value = 0
                                Vodafone_Idea_cnt_dict = {hr:Vodafone_Idea_tmp_value}
                                Vodafone_Idea_update_op_dict.update(Vodafone_Idea_cnt_dict)

                airtel_operator = list(Airtel_update_op_dict.values())
                other_operator = list(Others_update_op_dict.values())
                Reliance_operator = list(Reliance_update_op_dict.values())
                BSNL_MTNL_operator = list(BSNL_MTNL_update_op_dict.values())
                Vodafone_operator = list(Vodafone_Idea_update_op_dict.values())

                return airtel_operator,other_operator,Reliance_operator,BSNL_MTNL_operator,Vodafone_operator
        except Exception as err:
                log.error(str(err))
                traceback.print_exc()


def region_call_count_hour_data_set(df):
        try:
                df = df.groupby(['campaign_name','hour','date','datetime_combined','circle'])['time'].size().reset_index(name='count')
                # Assuming your DataFrame is named df
                df['hour'] = df['hour'].apply(lambda x: f'{x:02}')
                df = df.groupby(['hour','circle'])['count'].sum().reset_index(name='count')

                hour_list = []
                for tmp_hour in range(0,24):
                        # Check if the integer has a single digit
                        if isinstance(tmp_hour, int) and len(str(tmp_hour)) == 1:
                                tmp_hour = "0"+str(tmp_hour)
                                hour_list.append(tmp_hour)
                        else:
                                tmp_hour = str(tmp_hour)
                                hour_list.append(tmp_hour)

                # Convert DataFrame to the specified format
                formatted_data = {}
                for _, row in df.iterrows():
                        hour = str(row['hour'])
                        operator = row['circle']
                        count_value = row['count']

                        if hour not in formatted_data:
                                formatted_data[hour] = {}

                        formatted_data[hour][operator] = {'count value': count_value}
                data = formatted_data

                # Get all unique states from the data
                all_states = set()
                for hour, states in data.items():
                        all_states.update(states.keys())

                # Create a dictionary to store state-wise count lists (all hours initialized to 0)
                state_wise_counts = {state: [0] * 24 for state in all_states}

                # Populate counts based on actual data
                for hour, states in data.items():
                        for state, count_value in states.items():
                                count = count_value["count value"]
                                state_wise_counts[state][int(hour)] = count

                tmp_list = []
                state_list = []
                for state, counts in state_wise_counts.items():
                        ts = {
                                "name": state,
                                "type": "line",
                                "smooth": 0.6,
                                "stack": "Total",
                                "areaStyle": {},
                                "emphasis": {
                                        "focus": 'series'
                                },
                                "data": counts
                                # "color": "#FFD301"
                        }
                        tmp_list.append(ts)
                        state_list.append(state)
                return tmp_list,state_list
        except Exception as err:
                traceback.print_exc()
                log.error(str(err))


def over_all_call_count_hourly_data_set(df):
        try:
                over_all_call_count_data_set_df = df.groupby(['campaign_name','hour','date','datetime_combined'])['time'].size().reset_index(name='count')

                hour_list = []
                for tmp_hour in range(0,24):
                        # Check if the integer has a single digit
                        if isinstance(tmp_hour, int) and len(str(tmp_hour)) == 1:
                                tmp_hour = "0"+str(tmp_hour)
                                hour_list.append(tmp_hour)
                        else:
                                tmp_hour = str(tmp_hour)
                                hour_list.append(tmp_hour)


                over_all_call_count_data_set_df = over_all_call_count_data_set_df.groupby(['hour'])['count'].sum().reset_index(name='count')
                over_all_call_count_data_set_df['hour'] = over_all_call_count_data_set_df['hour'].astype(str)
                # Convert hour column to string and add "0" to single-digit values
                over_all_call_count_data_set_df['hour'] = over_all_call_count_data_set_df['hour'].apply(lambda x: f'0{x}' if len(str(x)) == 1 else str(x))

                # Convert DataFrame to dictionary
                result_dict = over_all_call_count_data_set_df.set_index('hour')['count'].to_dict()

                final_dict = {}
                for hr in hour_list:
                        if hr in result_dict.keys():
                                final_dict.update(result_dict)
                        else:
                                result_dict_1 = {hr:0}
                                final_dict.update(result_dict_1)

                formatted_data = [{"value": value, "name": name} for name, value in final_dict.items()]
                return formatted_data

        except Exception as err:
                log.error(str(err))
                traceback.print_exc()

def main_test(selected_campaign_name,start_date,end_date,selected_campaign_type):
        df = read_csv_files(selected_campaign_name,start_date,end_date,selected_campaign_type)

        # "===================================================================================="

        total_call_count_data_set_df = total_call_count_data_set(df)

        if not total_call_count_data_set_df.empty:
                total_call_count_data_set_df = total_call_count_data_set_df.to_dict(orient="records")
        else:
                total_call_count_data_set_df = [{'campaign_name': selected_campaign_name, 'count': 0}]

        # "===================================================================================="

        total_inbound_call_data_set_df,total_outbound_call_data_set_df = total_inbound_outbound_call_data_set(df)

        if not total_inbound_call_data_set_df.empty:
                total_inbound_call_data_set_df = total_inbound_call_data_set_df.to_dict(orient="records")
        else:
                total_inbound_call_data_set_df = [{"campaign_type": "INBOUND", "count": 0}]

        if not total_outbound_call_data_set_df.empty:
                total_outbound_call_data_set_df = total_outbound_call_data_set_df.to_dict(orient="records")
        else:
                total_outbound_call_data_set_df = [{"campaign_type": "OUTBOUND", "count": 0}]


        # "===================================================================================="

        auto_dial_df,preview_df,progressive_df = total_dialer_type_df_call_data_set(df)

        if not auto_dial_df.empty:
                auto_dial_df = auto_dial_df.to_dict(orient="records")
        else:
                auto_dial_df = [{'dialer_type': 'AUTO DIAL', 'count': 0}]

        if not preview_df.empty:
                preview_df = preview_df.to_dict(orient="records")
        else:
                preview_df = [{'dialer_type': 'PREVIEW', 'count': 0}]


        if not progressive_df.empty:
                progressive_df = progressive_df.to_dict(orient="records")
        else:
                progressive_df = [{'dialer_type': 'PROGRESSIVE', 'count': 0}]


        # "===================================================================================="

        region_data_set_df = region_data_set(df)

        if not region_data_set_df.empty:
                region_data_set_df = region_data_set_df.to_dict(orient="records")
        else:
                region_data_set_df = [{'circle': 'UP(East)', 'count': 0}]

        # "===================================================================================="

        success_failure_region_wise_data_set_df = success_failure_region_wise_data_set(df)

        if not success_failure_region_wise_data_set_df.empty:
                success_failure_region_wise_data_set_df = success_failure_region_wise_data_set_df.to_dict(orient="records")
        else:
                success_failure_region_wise_data_set_df = [{'call_status_disposition': 'answered', 'call_duration': 0, 'circle': 'UP(East)', 'hour': 00, 'datetime_combined': '2025-06-30 15:00:00'}]

        # "===================================================================================="

        operator_region_wise_data_set_df = operator_region_wise_data_set(df)

        if not operator_region_wise_data_set_df.empty:
                operator_region_wise_data_set_df = operator_region_wise_data_set_df.to_dict(orient="records")

        else:
                operator_region_wise_data_set_df = [{'circle': 'Reliance Jio', 'operator': 'Reliance Jio'}]

        # "===================================================================================="

        operator_data_set_df = operator_data_set(df)

        if not operator_data_set_df.empty:
                operator_data_set_df = operator_data_set_df.to_dict(orient="records")

        else:
                operator_data_set_df = [{'circle': 'Reliance Jio', 'operator': 'Reliance Jio'}]


        # "===================================================================================="

        success_failure_operator_wise_data_set_df = success_failure_operator_wise_data_set(df)


        if not success_failure_operator_wise_data_set_df.empty:
                success_failure_operator_wise_data_set_df = success_failure_operator_wise_data_set_df.to_dict(orient="records")

        else:
                success_failure_operator_wise_data_set_df = [{'call_status_disposition':'answered','call_duration':0,'operator':'Reliance Jio','hour':00}]

        # "===================================================================================="

        call_status_dis_operator_wise_data_set_df = call_status_dis_operator_wise_data_set(df)


        if not call_status_dis_operator_wise_data_set_df.empty:
                call_status_dis_operator_wise_data_set_df = call_status_dis_operator_wise_data_set_df.to_dict(orient="records")

        else:
                call_status_dis_operator_wise_data_set_df = [{'call_status_disposition':'answered','operator':'Reliance Jio'}]


        # "===================================================================================="

        over_all_call_status_dis_data_set_df = over_all_call_status_dis_data_set(df)


        if not over_all_call_status_dis_data_set_df.empty:
                over_all_call_status_dis_data_set_df = over_all_call_status_dis_data_set_df.to_dict(orient="records")
        else:
                over_all_call_status_dis_data_set_df = [{'call_status_disposition':'answered','count':0}]


        # "===================================================================================="


        airtel_operator,other_operator,Reliance_operator,BSNL_MTNL_operator,Vodafone_operator = operator_call_count_hour_data_set(df)

        # "===================================================================================="

        region_call_count_hour_data_set_df,state_list = region_call_count_hour_data_set(df)

        if len(state_list) == 0:
                state_list = ['UP(East)']


        if len(region_call_count_hour_data_set_df) == 0:
                region_call_count_hour_data_set_df = [{'name': 'UP(East)', 'type': 'line', 'smooth': 0.6, 'stack': 'Total', 'areaStyle': {}, 'emphasis': {'focus': 'series'}, 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}]


        # "===================================================================================="

        over_all_call_count_hourly_data_set_value = over_all_call_count_hourly_data_set(df)


        return [total_call_count_data_set_df,total_inbound_call_data_set_df,total_outbound_call_data_set_df,auto_dial_df,preview_df,progressive_df,region_data_set_df,success_failure_region_wise_data_set_df,operator_region_wise_data_set_df,operator_data_set_df,success_failure_operator_wise_data_set_df,call_status_dis_operator_wise_data_set_df,over_all_call_status_dis_data_set_df,airtel_operator,other_operator,Reliance_operator,BSNL_MTNL_operator,Vodafone_operator,over_all_call_count_hourly_data_set_value,region_call_count_hour_data_set_df,state_list]