import os
import sys
import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns


class MrtMapGenerator():
    def __init__(self, station_code):
        #0. Data Preparation
        print("MrtMapGenrator...")
        self.station_code = station_code

        self.regional_path = "geo_data/北北基桃.shp"
        self.district_path = 'geo_data/新北市區界_4.shp'
        self.tpe_path = 'geo_data/台北市區界.shp'

        self.mrt_route = 'geo_data/TpeMRTRoutes_WGS84_2.shp'
        self.mrt_pnt = 'station_code.csv'

        self.region = shp.Reader(self.regional_path)
        self.new_tpe = shp.Reader(self.district_path)
        self.sf_tpe = shp.Reader(self.tpe_path)
        self.mrt_r = shp.Reader(self.mrt_route,encoding="utf8")

    def get_df_max(self, df):
        max_value = 0
        for item in df.columns:
            if df[item].max() > max_value:
                max_value = df[item].max()
        return max_value

    #Get data from csv file generated from MRT_od_2_data_process.py
    def point_data_generator(self, colormap=None):
        result = {}
        if colormap == None:
            colormap = {'o':{'A':'#08306b',
                             'B':'#2171b5',
                             'C':'#6baed6',
                             'D':'#9ecae1'},
                        'd':{'A':'#67000d',
                             'B':'#cb181d',
                             'C':'#fc9272',
                             'D':'#fcbba1'}}
        else:
            colormap = colormap

        pnt_from = pd.read_csv('{}_od_result/df_from.csv'.format(self.station_code),
                                index_col=0,
                                encoding='utf-8',
                                engine='python')

        pnt_to = pd.read_csv('{}_od_result/df_to.csv'.format(self.station_code),
                            index_col=0,
                            encoding='utf-8',
                            engine='python')

        result['o'] = pnt_from
        result['d'] = pnt_to

        return result

    #Extract point location in shp file
    def point_generator(self, shape):
        x_lon = np.zeros((len(shape),1))
        y_lat = np.zeros((len(shape),1))
        for ip in range(len(shape)):
            x_lon[ip] = shape[ip][0]
            y_lat[ip] = shape[ip][1]
        return x_lon, y_lat

    #Draw polygon features such as districts and city area
    def plot_map(self, id ,sf, normal_color, line_color, line_width, x_lim = None, y_lim = None):
        main_fill = 'w'
        sub_fill = normal_color

        count = 0
        for shape in list(sf.iterShapes()):
            nparts = len(shape.parts) # total parts
            npoints=len(shape.points) # total points

            if nparts == 1:
                points = self.point_generator(shape.points)
                if count == id:
                    plt.plot(points[0],points[1], line_color, zorder=10, linewidth=line_width)
                    plt.fill(points[0],points[1], main_fill, zorder=10)
                else:
                    plt.plot(points[0],points[1], line_color, linewidth=line_width)
                    plt.fill(points[0],points[1], sub_fill)
                count += 1

            else:
                if count == id:
                    for ip in range(nparts): # loop over parts, plot separately
                        i0=shape.parts[ip]
                        if ip < nparts-1:
                            i1 = shape.parts[ip+1]-1
                        else:
                            i1 = npoints

                        seg=shape.points[i0:i1+1]
                        points = point_generator(seg)
                        plt.plot(points[0],points[1], line_color, zorder=10, linewidth=line_width)
                        plt.fill(points[0],points[1], main_fill, zorder=10)
                else:
                    for ip in range(nparts): # loop over parts, plot separately
                        i0=shape.parts[ip]
                        if ip < nparts-1:
                            i1 = shape.parts[ip+1]-1
                        else:
                            i1 = npoints

                        seg=shape.points[i0:i1+1]
                        points = self.point_generator(seg)
                        plt.plot(points[0],points[1], line_color, linewidth=line_width)
                        plt.fill(points[0],points[1], sub_fill)
                count += 1

        if (x_lim != None) & (y_lim != None):
            plt.xlim(x_lim)
            plt.ylim(y_lim)

    #Draw line feature, MRT routes in this case
    def plot_line(self, sf, line_color, line_width):
        count = 0
        for shape in list(sf.iterShapes()):
            nparts = len(shape.parts) # total parts
            npoints=len(shape.points) # total points

            if nparts == 1:
                points = self.point_generator(shape.points)
                if count == id:
                    plt.plot(points[0],points[1], line_color, zorder=10, linewidth=line_width)
                else:
                    plt.plot(points[0],points[1], line_color, linewidth=line_width)

                count += 1

            else:
                for ip in range(nparts): # loop over parts, plot separately
                    i0=shape.parts[ip]
                    if ip < nparts-1:
                        i1 = shape.parts[ip+1]-1
                    else:
                        i1 = npoints

                    seg=shape.points[i0:i1+1]
                    points = self.point_generator(seg)
                    plt.plot(points[0],points[1], line_color, zorder=10, linewidth=line_width)
                count += 1
    #Draw point data, mrt station in this case
    def plot_point(self, df, group, station, direction):
        legend_color = None
        legend_name_cluster = None
        legend_name_station = None
        for idx,row in df.iterrows():
            #direction "as destination"
            if direction == 'd':
                #Mark studied station
                if row['from'] == station:
                    plt.plot(row['long'],row['lat'],
                         marker='^',
                         markersize=13,
                         markeredgewidth=1,
                         markeredgecolor='k',
                         color='#f7fcb9',
                         zorder=14)
                    legend_name_station = '{} {}'.format(station, row['Eng'])

                #Mark specified station by cluster
                if row['cluster_group'] == group and row['from'] != station:
                    if legend_color == None:
                        legend_color = row['color']
                        legend_name_cluster = row['group_name']

                    plt.plot(row['long'],row['lat'],
                             marker='o',
                             markersize=7,
                             markeredgewidth=1,
                             markeredgecolor='k',
                             color=row['color'],
                             zorder=12)
                #Mark others
                elif row['cluster_group'] != group and row['from'] != station:
                    plt.plot(row['long'],row['lat'],
                             marker='o',
                             markersize=3,
                             markeredgewidth=1,
                             markeredgecolor='#969696',
                             color='#bdbdbd',
                             zorder=12)
            #direction "as orgin"
            else:
                if row['to'] == station:
                    plt.plot(row['long'],row['lat'],
                         marker='^',
                         markersize=13,
                         markeredgewidth=1,
                         markeredgecolor='k',
                         color='#f7fcb9',
                         zorder=14)
                    legend_name_station = '{} {}'.format(station, row['Eng'])

                if row['cluster_group'] == group and row['to'] != station:
                    if legend_color == None:
                        legend_color = row['color']
                        legend_name_cluster = row['group_name']

                    plt.plot(row['long'],row['lat'],
                             marker='o',
                             markersize=7,
                             markeredgewidth=1,
                             markeredgecolor='k',
                             color=row['color'],
                             zorder=12)
                elif row['cluster_group'] != group and row['to'] != station:
                    plt.plot(row['long'],row['lat'],
                             marker='o',
                             markersize=3,
                             markeredgewidth=1,
                             markeredgecolor='#969696',
                             color='#bdbdbd',
                             zorder=12)

        red_patch = mpatches.Patch(facecolor=legend_color, edgecolor='#000000', label=legend_name_cluster)
        station_patch = mpatches.Patch(facecolor='#f7fcb9', edgecolor='#000000', label='{}'.format(legend_name_station))
        plt.legend(handles=[station_patch, red_patch],prop={'size': 18},loc='lower right')


    #Draw point for gif usage, present with different size of radius according to the value
    def plot_point_gif(self, df, station, direction, max_val, pnt_size, i):
        #legend_name_station = None
        for idx,row in df.iterrows():
            #direction "as destination"
            if direction == 'd':
                #Mark studied station
                if row['from'] == station:
                    plt.plot(row['long'],row['lat'],
                            marker='^',
                            markersize=13,
                            markeredgewidth=1,
                            markeredgecolor='k',
                            color='#f7fcb9',
                            zorder=14)
                    legend_name_station = '{} {}'.format(station, row['Eng'])
                #Mark specified station by cluster
                else:
                    plt.plot(row['long'],row['lat'],
                             marker='o',
                             markersize= (row[i]/max_val)*pnt_size,
                             markeredgewidth=1,
                             markeredgecolor='k',
                             color='#cb181d',
                             alpha= 0.5,
                             zorder=12)
            elif direction == 'o':
                #Mark studied station
                if row['to'] == station:
                    plt.plot(row['long'],row['lat'],
                            marker='^',
                            markersize=13,
                            markeredgewidth=1,
                            markeredgecolor='k',
                            color='#f7fcb9',
                            zorder=14)
                    legend_name_station = '{} {}'.format(station, row['Eng'])
                #Mark specified station by cluster
                else:
                    plt.plot(row['long'],row['lat'],
                             marker='o',
                             markersize= (row[i]/max_val)*pnt_size,
                             markeredgewidth=1,
                             markeredgecolor='k',
                             color='#2171b5',
                             alpha= 0.5,
                             zorder=12)
        station_patch = mpatches.Patch(facecolor='#f7fcb9', edgecolor='#000000', label='{}'.format(legend_name_station))
        plt.legend(handles=[station_patch],prop={'size': 18},loc='lower right')

    # Module funtions for cluster map
    def mrt_cluster_map_generation(self, colormap=None):
        sys.stdout.write('\nGenerating cluster maps...')
        if colormap != None:
            colormap = colormap
        point_data = self.point_data_generator(colormap)
        for direction in point_data:
            for cluster in point_data[direction]['cluster_group'].unique():
                plt.figure(figsize = (15,12))
                ax = plt.axes() # add the axes
                ax.set_aspect('equal')
                plt.grid(False)
                plt.xticks([])
                plt.yticks([])

                #example: plot_map(id ,sf, normal_color, line_color, line_width, x_lim = None, y_lim = None)
                y_lim = (24.94,25.20) # latitude
                x_lim = (121.40, 121.65) # longitude
                self.plot_map('x',self.region,'#f0f0f0','#bdbdbd', 0.4)
                self.plot_map('x',self.new_tpe,'#f0f0f0','#d9d9d9', 0.4)
                self.plot_map('x',self.sf_tpe,'w', '#f0f0f0',0.6, x_lim, y_lim)
                self.plot_line(self.mrt_r,'#bdbdbd',0.9)

                self.plot_point(point_data[direction],cluster, self.station_code, direction)
                plt.savefig('{}_od_result/{}_{}_{}.png'.format(self.station_code,
                                                                 self.station_code,
                                                                 direction,
                                                                 cluster),
                            bbox_inches='tight')

    def file_checker(self, file_loc, package_name):
        original = os.getcwd()
        os.chdir(file_loc + '/' + self.station_code + '_od_result')
        dirName = package_name
        # Create target Directory if don't exist
        if not os.path.exists(dirName):
            os.mkdir(dirName)
            print("Directory " , dirName ,  " Created ")
        else:
            pass
            #print("Directory " , dirName ,  " already exists")
        os.chdir(original)

    #Module functions for gif map
    def mrt_gif_map_generation(self, directory, direction, max_circle, i):
        point_data = self.point_data_generator()
        plt.figure(figsize = (15,12))
        ax = plt.axes() # add the axes
        ax.set_aspect('equal')
        plt.grid(False)
        plt.xticks([])
        plt.yticks([])

        #example: plot_map(id ,sf, normal_color, line_color, line_width, x_lim = None, y_lim = None)
        y_lim = (24.94,25.20) # latitude
        x_lim = (121.40, 121.65) # longitude
        self.plot_map('x',self.region,'#f0f0f0','#bdbdbd', 0.4)
        self.plot_map('x',self.new_tpe,'#f0f0f0','#d9d9d9', 0.4)
        self.plot_map('x',self.sf_tpe,'w', '#f0f0f0',0.6, x_lim, y_lim)
        self.plot_line(self.mrt_r,'#bdbdbd',0.9)

        point_data_max = self.get_df_max(point_data[direction].iloc[:, :147])
        self.plot_point_gif(point_data[direction], self.station_code, direction, point_data_max, max_circle, i)

        file_subname_prefix = point_data[direction].columns
        title = file_subname_prefix[i].split('_')[0] + ' ' + file_subname_prefix[i].split('_')[1] + ":00"
        plt.figtext(0.25, 0.85, title, fontsize=20)
        plt.savefig('{}_od_result/{}/gif{}_{}_{}_{}.png'.format(self.station_code,
                                                                 directory,
                                                                 i,
                                                                 self.station_code,
                                                                 direction,
                                                                 file_subname_prefix[i]),
                    bbox_inches='tight')
        plt.close()
        sys.stdout.write('\rDirection {} {} is done'.format(direction ,title))

    def mrt_gif_bulk(self):
        dir_name_d = 'gif_d'
        dir_name_o = 'gif_o'
        self.file_checker(os.getcwd(), dir_name_d)
        self.file_checker(os.getcwd(), dir_name_o)
        count = 0
        for i in range(147):
            self.mrt_gif_map_generation(dir_name_d, 'd', 70, i)
            self.mrt_gif_map_generation(dir_name_o, 'o', 70, i)
