import pandas as pd
import os
import re
from sklearn.cluster import KMeans


class StationOdInsight:
    def __init__(self, slicer, source_file_location, num_clusters, created_package_name):
        self.slicer = slicer
        if self.slicer[-1] == '_':
            self.direction = 'from'
            self.station = self.slicer.split('_')[0]
        else:
            self.direction = 'to'
            self.station = self.slicer.split('_')[1]

        self.source_file_location = source_file_location
        self.num_clusters = num_clusters

        self.od_daily = {} #people count of daily average for each od
        self.total_daily = 0 #daily total people for given direction
        self.accumu_sum = {} # accumulating people by od using sorted list (from largest od to smallest)
        self.accumu_ratio = {} # ratio version of previous step

        self.cluster = {}
        ##Keys in self.cluster:
        #raw = {} # od with its original cluster (ex 0, 1, 2)
        #checker = {} #group ods by its kmeans cluster
        #people = {} #daily total people of each cluster group
        #station = {} #number of station in each cluster group
        #station_avg = {} #avg people of each station in each cluster group

        self.heatmap_data = {} #normalize table used for heatmap visualization
        self.colormap = {'o':{'A':'#08306b',
                              'B':'#2171b5',
                              'C':'#6baed6',
                              'D':'#9ecae1'},
                         'd':{'A':'#67000d',
                              'B':'#cb181d',
                              'C':'#fc9272',
                              'D':'#fcbba1'}}


        self.groupmap = {'o':{0:'A',
                              1:'B',
                              2:'C',
                              3:'D'},
                         'd':{0:'A',
                              1:'B',
                              2:'C',
                              3:'D'}}
        self.max_people_hr = {}


        # Create target Directory if don't exist
        if not os.path.exists(created_package_name):
            os.mkdir(created_package_name)
            print("Directory " , created_package_name ,  " Created ")
        else:
            print("Directory " , created_package_name ,  " already exists")

        self.output_location = './{}'.format(created_package_name)

    ## Attribute handler
    def setColorMap(self, dict_):
        print('set colormap')
        self.colormap = dict_

    def cluster_key_changer(self, to_be_changed, changer):
        #change key in dictionary:
        #https://stackoverflow.com/questions/4406501/change-the-name-of-a-key-in-dictionary

        #to_be_changed format example : {1: 56884.05000000002, 0: 68918.31999999999, 2: 28883.590000000004}
        #changer example: group_mapO = {0:'A',1:'B', 2:'C'}
        out_put = to_be_changed
        for old_k,new_k in changer.items():
            for original_k, v in out_put.items():
                if old_k == original_k:
                    out_put[new_k] = out_put.pop(original_k)
        return out_put

    #Define cluster name by pattern shown in the cluster
    def setGroupMap(self, dict_):
        print('reset cluster groupmap name')
        if self.direction == 'from':
            dict_ = dict_['o']
        else:
            dict_ = dict_['d']

        self.cluster['station'] = self.cluster_key_changer(self.cluster['station'], dict_)
        self.cluster['station_avg'] = self.cluster_key_changer(self.cluster['station_avg'], dict_)
        self.cluster['people']['count'] = self.cluster_key_changer(self.cluster['people']['count'], dict_)
        self.cluster['people']['ratio'] = self.cluster_key_changer(self.cluster['people']['ratio'], dict_)
        self.cluster['checker'] = self.cluster_key_changer(self.cluster['checker'], dict_)
        self.heatmap_data = self.cluster_key_changer(self.heatmap_data, dict_)
        self.max_people_hr = self.cluster_key_changer(self.max_people_hr, dict_)
        self.result_df(dict_)


    ## Basic function
    def get_df_max(self, df):
        max_value = 0
        for item in df.columns:
            if df[item].max() > max_value:
                max_value = df[item].max()
                max_index = df[item].idxmax()
                max_cols = item
                max_loc = (max_index,max_cols)
        return max_value, max_loc

    def normalize_df(self, df):
        return round(df/self.get_df_max(df)[0],2)*100

    def station_table_to_list(self, station_sum_up, normalize_on):
        #1 Normalizing data
        if normalize_on == 'normalize':
            normalize = round(station_sum_up/self.get_df_max(station_sum_up)[0],2)
        else:
            normalize = station_sum_up
        #2 Transform to a list of lists
        middle_list = normalize.values.tolist()
        #3 Transform to a single list
        result_list = [item for sub in middle_list for item in sub]

        return result_list

    ##I. DATA PREPARATION
    #1. Get target od from data_generator.  pattern example: 'BL11_' or '_BL11'
    def data_getter(self, slicer, file_location):
        od_dict = {}
        od_sum_dict = {}

        print('slicer in data_getter: {}'.format(slicer))
        for filename in os.listdir(file_location):
            if slicer[0] == '_':
                pattern = re.compile('{}$'.format(slicer))
                if re.search(pattern, filename[:-4]):
                    df = pd.read_csv('{}/{}'.format(file_location,filename),
                                     index_col=0,
                                     skiprows=[0,2],
                                     engine='python')
                    #station total traffic
                    od_sum = round(df.values.sum()/7,2)
                    #-4 for skipping file format, ".csv"
                    od_sum_dict[filename[:-4]] = od_sum

                    lst = self.station_table_to_list(df,'normalize')
                    od_dict[filename[:-4]] = lst

            else:
                if re.match(slicer, filename):
                    df = pd.read_csv('{}/{}'.format(file_location,filename),
                                     index_col=0,
                                     skiprows=[0,2],
                                     engine='python')

                    od_sum = round(df.values.sum()/7,2)
                    od_sum_dict[filename[:-4]] = od_sum

                    lst = self.station_table_to_list(df,'normalize')
                    od_dict[filename[:-4]] = lst
        self.od_daily = od_sum_dict

        return od_dict

    #2. Kmeans process.
    def k_means(self, dict_, num_clusters):
        df_station_od = pd.DataFrame.from_dict(dict_).T
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(df_station_od)
        df_station_od['cluster'] = kmeans.labels_

        return df_station_od['cluster']

    #3. Create od cluster group.
    def cluster_by_od(self, df_cluster_col):
        cluster_dict = {}
        for item in df_cluster_col.iteritems():
            cluster_dict.setdefault(item[1], []).append(item[0])
        self.cluster['checker'] = cluster_dict
        return cluster_dict

    #4. Create classified tables reading from files.
    def heatmap_data_dict(self, cluster_dict):
        for_heatmap = {}
        max_people = {}
        for key in cluster_dict.keys():
            cluster_ods = {}
            max_ods = {}
            for od in cluster_dict[key]:
                #https://blog.csdn.net/ArcheriesYe/article/details/77992412
                df = pd.read_csv('{}/{}.csv'.format(self.source_file_location,od),
                                 index_col=0,
                                 skiprows=[0,2],
                                 engine='python')
                df_max = self.get_df_max(df)
                df = self.normalize_df(df)
                cluster_ods[od] = df
                max_ods[od] = df_max
            for_heatmap[key] = cluster_ods
            max_people[key] = max_ods

        print("Cluster result: {}".format([len(for_heatmap[x]) for x in for_heatmap]))

        self.heatmap_data = for_heatmap
        self.max_people_hr = max_people

    def ratio_calc(self, od_daily):
        sorted_od_daily = sorted(od_daily.items(), key=lambda kv: kv[1],reverse=True)
        total_avg = 0
        people_sum_dict = {}
        people_ratio_dict = {}
        for i in range(len(sorted_od_daily)):
            total_avg += sorted_od_daily[i][1]
            people_sum_dict[i+1] = total_avg
        for k,v in people_sum_dict.items():
            people_ratio_dict[k] = round(v/total_avg,3)

        self.total_daily = total_avg
        self.accumu_sum = people_sum_dict
        self.accumu_ratio = people_ratio_dict

    def cluster_ppl(self):
        data = {}
        data_count = {}
        data_ratio = {}
        total = 0
        #Count people by cluster.
        for cluster in self.cluster['checker']:
            data_count[cluster] = 0
            for od in self.cluster['checker'][cluster]:
                data_count[cluster] += round(self.od_daily[od],3)
            total += data_count[cluster]
        #data['total'] = total

        for cluster in data_count:
            data_ratio[cluster] = round(data_count[cluster]/total,3)

        data['count'] = data_count
        data['ratio'] = data_ratio

        self.cluster['people'] = data

    def cluster_station_generator(self):
        data = {}
        for k in self.cluster['checker']:
            data[k] = len(self.cluster['checker'][k])

        self.cluster['station'] = data

    def cluster_station_avg_generator(self):
        data = {}
        for cluster in self.cluster['people']['count']:
            people = self.cluster['people']['count'][cluster]
            station = self.cluster['station'][cluster]
            station_avg = round(people/station,2)
            data[cluster] = station_avg

        self.cluster['station_avg'] = data

    def rename_dict(self):
        headers = []
        for weekday in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']:
            for workinghours in ['00','01','05','06','07','08','09',
                                 '10','11','12','13','14','15','16',
                                 '17','18','19','20','21','22','23']:
                headers.append(weekday + '_' + workinghours)

        rename_dict = {}
        for i in range(147):
            rename_dict[i] = headers[i]
        rename_dict[147] = 'cluster_group'
        rename_dict[148] = 'daily_ppl_avg'
        rename_dict[149] = 'max_people_by_hr'
        rename_dict[150] = 'max_weekday'
        rename_dict[151] = 'max_hour'
        return rename_dict

    def result_df(self, group_map):
        od_dict = {}
        for cluster in self.heatmap_data:
            for od, data in self.heatmap_data[cluster].items():
                raw_data = self.heatmap_data[cluster][od]
                max_people_hourly = self.max_people_hr[cluster][od][0]
                refined_data = self.station_table_to_list(round(raw_data/100*max_people_hourly,2),'-')
                refined_data.extend((self.cluster['raw'][od],self.od_daily[od]))

                for cluster_in_max,od_under_cluster in self.max_people_hr.items():
                    for od_in_max,v in od_under_cluster.items():
                        if od_in_max == od:
                            refined_data.extend((v[0],v[1][0],v[1][1]))


                od_dict[od] = refined_data


        df_test = pd.DataFrame.from_dict(od_dict).T
        #https://stackoverflow.com/questions/12504976/get-last-column-after-str-split-operation-on-column-in-pandas-dataframe

        df_test['to'] = df_test.index.str.split('_').str[-1]
        df_test['from'] = df_test.index.str.split('_').str[-0]

        df_test = df_test.rename(columns = self.rename_dict())

        ##
        if self.direction == 'from':
            colormap = self.colormap['o']
            df_test['group_name'] = df_test['cluster_group'].map(group_map)
            df_test['color'] = df_test['group_name'].map(colormap)
        else:
            colormap = self.colormap['d']
            df_test['group_name'] = df_test['cluster_group'].map(group_map)
            df_test['color'] = df_test['group_name'].map(colormap)
        ##

        mrt_pnt = 'station_code.csv'
        mrt_p = pd.read_csv(mrt_pnt,index_col=0,encoding='utf-8')
        if self.direction == 'from':
            df_test = df_test.merge(mrt_p[['lat','long','code','Eng','站名']],left_on='to',right_on='code')
        else:
            df_test = df_test.merge(mrt_p[['lat','long','code','Eng','站名']],left_on='from',right_on='code')

        df_test.to_csv('{}/{}_{}.csv'.format(self.output_location,'df',self.direction),encoding='utf-8')

    def prepare_data(self):
        print("processing {} with {} clusters".format(self.slicer, self.num_clusters))
        raw_data = self.data_getter(self.slicer, self.source_file_location)

        k_result = self.k_means(raw_data, self.num_clusters)
        self.cluster['raw'] = k_result.to_dict()

        cluster_dictionary = self.cluster_by_od(k_result)
        self.heatmap_data_dict(cluster_dictionary)

        self.cluster_ppl()
        self.cluster_station_generator()
        self.cluster_station_avg_generator()
        self.ratio_calc(self.od_daily)
        self.setGroupMap(self.groupmap)
