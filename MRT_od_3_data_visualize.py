import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import sys
import random

sns.set()

class StationOdVisualize():
    def __init__(self, data_object):
        self.station = data_object.station
        self.direction = data_object.direction
        self.output_location = data_object.output_location
        self.heatmap_data = data_object.heatmap_data

        self.groupmap = data_object.groupmap
        self.colormap = data_object.colormap
        self.cluster = data_object.cluster
        self.od_daily = data_object.od_daily

    def random_key_selector(self, selected_dict, select_num):
        key_list = []
        for i in range(select_num):
            key = random.choice(list(selected_dict))
            #make sure no dulplicates
            while key in key_list:
                key = random.choice(list(selected_dict))
            key_list.append(key)
        return key_list

    def example_data_generator(self, select_dict,key_list):
        result = {}
        for key in key_list:
            result[key] = select_dict[key]
        return result

    #1. For plt namings.
    def station_eng_name(self):
        file_ID = 'station_name.csv'
        with open(file_ID, 'r', encoding="utf-8") as fid:
            stationlist = csv.reader(fid)
            id_dict = {rows[0]:rows[3] for rows in stationlist}
        return id_dict

    #2. Heatmap generator.
    def heat_map(self, col_num, example):
        print('\nGenerating Heatmap...')
        direction = None
        if self.direction == 'from':
            direction = 'from'
            color = 'Blues'
        else:
            direction = 'to'
            color = 'Reds'

        english_name = self.station_eng_name()
        for cluster in self.heatmap_data:

            example_figs = 10
            if example == True:
                ran_key = self.random_key_selector(self.heatmap_data[cluster], example_figs)
                group_dict_adjust = self.example_data_generator(self.heatmap_data[cluster], ran_key)
                sys.stdout.write('\rprocessing cluster Demo: {}, taking {} from cluster length: {}\n'.format(cluster,example_figs,len(self.heatmap_data[cluster])))

            else:
                group_dict_adjust = self.heatmap_data[cluster]
                sys.stdout.write('\rprocessing cluster: {}, cluster length: {}\n'.format(int(cluster),len(group_dict[cluster])))


            #Set figure size according to number of dataframe in that cluster
            if len(group_dict_adjust) % col_num == 0:
                   heigh = int(len(group_dict_adjust)/col_num)
            else:
                   heigh = int(len(group_dict_adjust)/col_num) + 1

            fig, ax = plt.subplots(heigh,col_num,figsize = (12*col_num,6*heigh))
            fig.subplots_adjust(hspace = .3)

            cbar_ax = fig.add_axes([.91, .3, .01, .2])
            count = 0
            for item in group_dict_adjust:
                #col_num yx, or high xy depends on how you want maps to be ordered, right to left and next row,
                # or top to bottom and next column
                location_y = int(count%col_num)
                location_x = int(count/col_num)
                sys.stdout.write('\rprocessing {} ax[{}, {}]'.format(count,location_x,location_y))
                station_code = None
                #get station name
                if direction == 'from':
                    station_code = item.split('_')[1]
                elif direction == 'to':
                    station_code = item.split('_')[0]
                for k,v in english_name.items():
                    if k == station_code:
                        station_name = v

                # ax index with reference to:
                # https://stackoverflow.com/questions/49809027/matplotlib-subplots-too-many-indices-for-array
                try:
                    heatmap = sns.heatmap(group_dict_adjust[item],center=None,
                                          ax = ax[location_x,location_y],
                                          cbar=count == 0,
                                          cmap=color,
                                          vmin= 0,
                                          vmax= 100,
                                          annot=True,
                                          cbar_ax=None if count else cbar_ax,
                                          fmt='g')
                    if direction == 'from':
                        ax[location_x,location_y] \
                        .set_title('{}: to {} (% by hourly max))'.format(item,
                                                                         station_name),y=1.1)

                    elif direction == 'to':
                        ax[location_x,location_y] \
                        .set_title('{}: from {} (% by hourly max)'.format(item,
                                                                           station_name),y=1.1)

                    ax[location_x,location_y].xaxis.tick_top()
                    ax[location_x,location_y].set_xlabel('Time of Day')
                    count += 1

                except IndexError:
                    heatmap = sns.heatmap(group_dict_adjust[item],center=None,
                                          ax = ax[count],
                                          cbar=count == 0,
                                          cmap=color,
                                          vmin= 0,
                                          vmax= 100,
                                          annot=True,
                                          cbar_ax=None if count else cbar_ax,
                                          fmt='g')
                    if direction == 'from':
                        ax[count].set_title('{}' \
                            .format('{}: to {} (%)'.format(item,station_name)),y=1.1)
                    elif direction == 'to':
                        ax[count].set_title('{}' \
                            .format('{}: from {} (%)'.format(item,station_name)),y=1.1)
                    ax[count].xaxis.tick_top()
                    ax[count].set_xlabel('Time of Day')
                    count += 1
            if example == True:
                plt.savefig('{}/Demo_{}_{}_{}.png'.format(self.output_location,self.station,direction,cluster), bbox_inches='tight')
            else:
                plt.savefig('{}/{}_{}_{}.png'.format(self.output_location,self.station,direction,cluster), bbox_inches='tight')

    def bar_ranking(self, topN):
        print('\nGenerating Bar Graph...')
        sorted_od_daily = sorted(self.od_daily.items(), key=lambda kv: kv[1],reverse=True)
        top = sorted_od_daily[:topN]
        direction = None
        color = None
        sub_title = None
        x_label = None
        data = {}
        count = 0

        for item in top:
            single_dict = {}
            if self.direction == 'from':
                single_dict['name'] = item[0].split('_')[1]
                direction = 'from'
                sub_title = 'as Origin'
                x_label = 'Destination'
                color_map = self.colormap['o']
                used_group_map = self.groupmap['o']

            else:
                single_dict['name'] = item[0].split('_')[0]
                direction = 'to'
                sub_title = 'as Destination'
                x_label = 'Origin'
                color_map= self.colormap['d']
                used_group_map = self.groupmap['d']

            single_dict['value'] = item[1]

            #get cluster group
            for k,v in self.cluster['raw'].items():
                if k == item[0]:
                    single_dict['group'] = v
            data[count] = single_dict
            count += 1


        plt.figure(1, figsize=(9, 5))
        plt.grid(axis='y',linestyle='--', zorder=0)

        y_pos = np.arange(len(data.keys()))

        df=pd.DataFrame.from_dict(data,orient='index')
        df['group_name'] = df['group'].map(used_group_map)
        df['colors'] = df["group_name"].map(color_map)

        for g in df['group_name'].unique():
            xs=df.index[df["group_name"]==g]
            ys=df["value"][df["group_name"]==g]
            color=df["colors"][df["group_name"]==g]
            plt.bar(xs,ys,color=color,label=g)

        plt.xticks(y_pos,df['name'],rotation='45')
        plt.xlabel('{}'.format(x_label))
        plt.ylabel('People')
        plt.title('Traffic of ODs ({} {})'.format(self.station,sub_title))
        plt.legend()
        plt.savefig('{}/{}_{}.png'.format(self.output_location,'Bar',direction), bbox_inches='tight')
        plt.clf()

    def cluster_key_changer(self, to_be_changed, changer):
        #change key in dictionary:
        #https://stackoverflow.com/questions/4406501/change-the-name-of-a-key-in-dictionary
        out_put = to_be_changed
        for old_k,new_k in changer.items():
            for original_k, v in out_put.items():
                if old_k == original_k:
                    out_put[new_k] = out_put.pop(original_k)
        return out_put

    def pie_chart(self):
        print('\nGenerating Pie Graph...')
        if self.direction == 'from':
            used_color_map = self.colormap['o']
        else:
            used_color_map = self.colormap['d']

        fig1, ax1 = plt.subplots()

        pie_data = self.cluster['people']['ratio']
        wedges, texts, autotexts = ax1.pie([v for v in pie_data.values()],
                                            labels=[k for k in pie_data.keys()],
                                            colors=[used_color_map[v] for v in pie_data.keys()],
                                            autopct='%1.1f%%', shadow=True, startangle=90)
        #Pie chart text settings:
        #https://stackoverflow.com/questions/27898830/python-how-to-change-autopct-text-color-to-be-white-in-a-pie-chart
        for autotext in autotexts:
            autotext.set_color('white')

        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.set_title('Ratio of Average Daily People in Each Cluster')
        plt.savefig('{}/{}_{}.png'.format(self.output_location,'Pie',self.direction), bbox_inches='tight')
        #plt.show()
