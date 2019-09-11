from MRT_od_1_data_generator import StationOdGenerator
from MRT_od_2_data_process import StationOdInsight
from MRT_od_3_data_visualize import StationOdVisualize
from MRT_od_4_data_map import MrtMapGenerator

class StationRunner():
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.station_code = input("Please type the station code (ex. BL12): ")
        self.output_folder_name = "{}_od_result".format(self.station_code)
        self.num_clusters = 3
        self.od_generator = StationOdGenerator(raw_data=self.raw_data,
                                               station_code=self.station_code)

        self.od_insight_from = StationOdInsight(slicer=self.station_code+'_',
                                                source_file_location=self.od_generator.output_folder_name,
                                                num_clusters=self.num_clusters,
                                                created_package_name=self.output_folder_name)

        self.od_insight_to = StationOdInsight(slicer='_'+self.station_code,
                                              source_file_location=self.od_generator.output_folder_name,
                                              num_clusters=self.num_clusters,
                                              created_package_name=self.output_folder_name)

        self.od_generator.od_by_station()
        self.od_insight_from.prepare_data()
        self.od_insight_to.prepare_data()

    def visualized(self,insight_object):
        print("Visualizing...")
        self.od_vis = StationOdVisualize(insight_object)
        self.od_vis.bar_ranking(topN=20)
        self.od_vis.heat_map(col_num=2, example=True)
        self.od_vis.pie_chart()

    def geo_visualized(self, station_code):
        self.od_geo = MrtMapGenerator(station_code)
        self.od_geo.mrt_cluster_map_generation()
        self.od_geo.mrt_gif_bulk()


if __name__ == "__main__":
    runner = StationRunner("201806_MRT_hourly.csv")
    runner.visualized(runner.od_insight_from)
    runner.visualized(runner.od_insight_to)
    runner.geo_visualized(runner.station_code)
    print("\nDone")
