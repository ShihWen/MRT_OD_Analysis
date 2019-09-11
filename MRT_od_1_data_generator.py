import pandas as pd
import datetime
import sys
import os

class StationOdGenerator():
    def __init__(self, raw_data, station_code):
        print("StationOdGenerator...")
        try:
            self.df_raw = pd.read_csv(raw_data)
            self.dtype_setting(self.df_raw)
        except FileNotFoundError:
            self.df_raw = None

        self.station_code = station_code
        self.output_folder_name = '{}_OD_folder'.format(self.station_code)

    def dtype_setting(self, df):
        print('converting first 5 dtypes...')
        df['date'] = pd.to_datetime(df['date'])
        df["time"] = df["time"].astype('int8')
        df["people"] = pd.to_numeric(df["people"], downcast='integer')
        df["entrance"] = df["entrance"].astype('category')
        df["exit"] = df["exit"].astype('category')
        print('processing IDs...')
        df["code_entrance"] = df["code_entrance"].astype('category')
        df["code_exit"] = df["code_exit"].astype('category')
        df['code_from_to'] = df['code_from_to'].astype('category')
        df['from_to'] = df['from_to'].astype('category')

        print('processing datetime, weeknum and weekday...')
        df["weekday"] = pd.to_numeric(df["weekday"], downcast='integer')
        df["weeknum"] = pd.to_numeric(df["weeknum"], downcast='integer')


    def create_od_table(self, df, od):
        df_processed = df.groupby(['code_from_to','weekday', 'time'],as_index=False).aggregate({'people':'mean'})
        od_table = pd.pivot_table(df_processed[df_processed['code_from_to']== od],index='weekday',columns='time')
        od_table['weekday'] = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        od_table = od_table.set_index('weekday')
        return od_table


    def od_by_station(self):
        if self.df_raw != None:
            start = datetime.datetime.now()

            # Create target Directory if don't exist
            if not os.path.exists(self.output_folder_name):
                os.mkdir(self.output_folder_name)
                print("Directory " , self.output_folder_name ,  " Created ")
            else:
                print("Directory " , self.output_folder_name ,  " already exists")


            df_station = self.df_raw[self.df_raw['code_from_to'].str.contains(self.station_code)]
            od_list = self.df_raw['code_from_to'][self.df_raw['code_from_to'].str.contains(self.station_code)].unique()

            count = 1
            for od in od_list:
                percentage = str(round(count/len(od_list)*100,2))
                sys.stdout.write('\rprocessing table {}, {} % completed.'.format(od, percentage))
                if os.path.isfile('{}/{}.csv'.format(self.output_folder_name, od)) == False:
                    od_table = self.create_od_table(self.df_raw, od)
                    od_table.to_csv('{}/{}.csv'.format(self.output_folder_name, od))

                count += 1

            total_time = datetime.datetime.now() - start
            print('\nRuntime for the process: {}'.format(total_time))
            print('Done')
        else:
            print('Raw file not exist, checking if the od file has been created...')
