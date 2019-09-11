# MRT OD Analysis
Analyze all the origin-destination patterns with given single station, using Tapei Main Station (code BL12) as an example with K as 3 based on the result from [MRT_od_5_suggest_K_by_elbow.ipynb](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/MRT_od_5_suggest_K_by_elbow.ipynb).</br>
You can also read the related article on my [Medium](https://medium.com/@shihwenwutw/%E9%80%8F%E9%81%8E%E6%97%85%E6%AC%A1%E7%B5%84%E6%88%90%E8%A7%A3%E6%9E%90%E5%8F%B0%E5%8C%97%E8%BB%8A%E7%AB%99%E4%BA%BA%E6%B5%81-e8bde91eadb1) for reference.

Extended from [_MRT_Cleaning_Visualizing_](https://github.com/ShihWen/MRT_Cleaning_Visualizing), here we will use data generated by MRT_cleaning_visualizing.ipynb, and run MRT_od_runner.py, which is consist of:
- MRT_od_1_data_generator.py: Create hourly table for all od combinations of given station
- MRT_od_2_data_process.py: Prepare data for Kmeans, generateresult table, and calculate a number of variables for visualization and reference
- MRT_od_3_data_visualize.py: Generate bar graph, heat map and pie chart for reference.
- MRT_od_4_data_map.py: Geo-visualize data in terms of cluster result and number of people.

Below is the processing flow:
</br>
![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/image/process_flow.png)


Types of data:

|Raw Data|Cleaned Data|OD data|
| :-------------: |:-------------:| :-----:|
| ![](https://github.com/ShihWen/MRT_Cleaning_Visualizing/blob/master/images/1_raw_data.png)|![](https://github.com/ShihWen/MRT_Cleaning_Visualizing/blob/master/images/2_cleaned_data.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/image/od_data.png)|


Heatmap by cluster:

- Taipei Main Station as origin:

|Cluster A|Cluster B|Cluster C|
| :-------------: |:-------------:| :-----:|
| ![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Demo_BL12_from_A.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Demo_BL12_from_B.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Demo_BL12_from_C.png)|

- Taipei Main Station as destination:

|Cluster A|Cluster B|Cluster C|
| :-------------: |:-------------:| :-----:|
| ![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Demo_BL12_to_A.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Demo_BL12_to_B.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Demo_BL12_to_C.png)|

Bar graph showing the top 20 based on daily average people:

|Taipei Main Station as Origin|Taipei Main Station as Destination|
| :-------------: |:-------------:|
| ![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Bar_from.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Bar_to.png)|

Pei chart showing the ratio of people in each cluster group:

|Taipei Main Station as Origin|Taipei Main Station as Destination|
| :-------------: |:-------------:|
| ![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Pie_from.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/Pie_to.png)|

</br>
Present the result on the map by cluster groups:

- Taipei Main Station as origin:

|Cluster A|Cluster B|Cluster C|
| :-------------: |:-------------:| :-----:|
| ![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/BL12_o_0.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/BL12_o_1.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/BL12_o_2.png)|

- Taipei Main Station as destination:

|Cluster A|Cluster B|Cluster C|
| :-------------: |:-------------:| :-----:|
| ![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/BL12_d_0.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/BL12_d_1.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/BL12_d_2.png)|

</br>
Present the result on the map by number of people:

- Taipei Main Station as Origin

|8 a.m. on Thursday|6 p.m. on Thursday|
| :-------------: |:-------------:|
| ![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/gif_o/gif68_BL12_o_Thu_08.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/gif_o/gif78_BL12_o_Thu_18.png)|


- Taipei Main Station as Destination

|8 a.m. on Thursday|6 p.m. on Thursday|
| :-------------: |:-------------:|
| ![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/gif_d/gif68_BL12_d_Thu_08.png)|![](https://github.com/ShihWen/MRT_OD_Analysis/blob/master/BL12_od_result/gif_d/gif78_BL12_d_Thu_18.png)|
