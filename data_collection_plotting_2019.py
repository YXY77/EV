#Import required python built-in lib.
import geopandas as gpd
import numpy as np
import mapclassify
import pandas as pd
import matplotlib.pyplot as plt

#importing the map-data of Washington 
usa = gpd.read_file('./gadm36_USA_shp/gadm36_USA_2.shp')
Washington=usa.loc[usa.NAME_1.isin(['Washington']),['NAME_2','geometry']]
Washington.columns = ['County','geometry']

#Data import
data1=pd.read_csv('./data/Electric_Vehicle_Population_Data_1.csv') #dependent variable
data3=pd.read_csv('./data/GHG_Reporting_Program_Publication.csv') #Air Pollution
data6=pd.read_csv('./data/income_2019.csv')                       #Income
data7=pd.read_csv('./data/Job_population_per_county_2019.csv')    #Number of Employment
data8=pd.read_csv('./data/Population_county_2019.csv')            #Population

#Data Preprocessing for Data collected in 2019
#(1)Creating new DataFrame for the dependent vaiable, i.e. number of EV per County.
df_EV= {'County' : data1.loc[data1['Model Year']==2019]['County'].value_counts().index,
            'EV_number': data1.loc[data1['Model Year']==2019]['County'].value_counts()
           }
df_EV=pd.DataFrame(df_EV)


#(2)Creating new DataFrame for the pollution-realted vaiables
pollution=data3[data3['Year']==2019].groupby('County').mean().to_numpy()[:,2:7]
data3_county=data3[data3['Year']==2019].groupby('County').mean().index.to_numpy()
df_pollution={'County':data3_county,
              'Total Emissions':pollution[:,0],
              'Biogenic Carbon Dioxide':pollution[:,1],
              'Carbon Dioxide':pollution[:,2],
              'Methane':pollution[:,3],
              'Nitrous Oxide':pollution[:,4]
}
df_pollution=pd.DataFrame(df_pollution)


#(3)Creating new DataFrame for the income, number of employment, and population
#(3.1)Collecting the Name of County in WA
data6_county=data6['GeoName'].unique()[1:40]
for i in range(len(data6['GeoName'].unique()[1:40])):
    data6_county[i]=data6_county[i][:-4]
    
#(3.2)COllecting the data of those variables
income=data6.loc[data6.GeoName.isin(data6['GeoName'].unique()[1:40])].groupby('GeoName').mean()['Income']
N_employment=data7.loc[data7.GeoName.isin(data7['GeoName'].unique()[1:40])].groupby('GeoName').mean()['N_Employment']
Population=data8.loc[data8.GeoName.isin(data8['GeoName'].unique()[1:40])].groupby('GeoName').mean()['Population']

#(3.3) Creating DataFrame
df_income_employment_population= {'County' : data6_county, 
                                  'Income': income,
                                  'Number of Employment':N_employment,
                                  'Population':Population,
                                 }
df_income_employment_population=pd.DataFrame(df_income_employment_population)


#(4)Merging the data and map-data (With Filling the Nan point by 0)
Washington = Washington.merge(df_EV, how='outer',on='County').fillna(0)
Washington = Washington.merge(df_pollution, how='outer',on='County').fillna(0)
Washington = Washington.merge(df_income_employment_population, how='outer',on='County').fillna(np.nan)


#Plotting function
def plotting_map(Washington,variable_name):
    fig, ax = plt.subplots(1, figsize=(10, 6), dpi=200)

    Washington.plot(
        column=variable_name, cmap='OrRd', scheme='FisherJenks', linewidth=0.5, edgecolor='0.5', ax=ax)
    ax.axis('off')


    #Adding colorbar

    # Create colorbar as a legend 
    sm = plt.cm.ScalarMappable(cmap='OrRd')
    # add the colorbar to the figure 
    cbar = fig.colorbar(sm)

    bins = mapclassify.FisherJenks(Washington[variable_name], 5).bins
    bins = np.insert(bins, 0, 0)
    _ = cbar.ax.set_yticklabels(bins)

    #Adding name of county
    for index, row in Washington.iterrows():
        xy = row['geometry'].centroid.coords[:]
        xytext = row['geometry'].centroid.coords[:]
        ax.annotate(row['County'], xy=xy[0], xytext=xytext[0],
                     horizontalalignment='center', verticalalignment='center', fontsize=5)
    if 'Number' in variable_name:
        ax.set_title('The '+variable_name+' in Washington', fontdict={
                 'fontsize': '16', 'fontweight': '1'})
    else:
        ax.set_title('The Number of '+variable_name+' in Washington', fontdict={
                     'fontsize': '16', 'fontweight': '1'})
    plt.savefig(variable_name+'.png')


def plotting_cluster(Washington,variable_name):
    fig, ax = plt.subplots(1, figsize=(10, 6), dpi=200)

    Washington.plot(
        column=variable_name, cmap='Spectral', scheme='FisherJenks', linewidth=0.5, edgecolor='0.5', ax=ax)
    ax.axis('off')


    #Adding colorbar

    # Create colorbar as a legend 
    sm = plt.cm.ScalarMappable(cmap='Spectral')
    # add the colorbar to the figure 
    cbar = fig.colorbar(sm)

    bins = mapclassify.FisherJenks(Washington[variable_name]+1, 5).bins
    bins = np.insert(bins, 0, 0)
    _ = cbar.ax.set_yticklabels(bins)

    #Adding name of county
    for index, row in Washington.iterrows():
        xy = row['geometry'].centroid.coords[:]
        xytext = row['geometry'].centroid.coords[:]
        ax.annotate(row['County'], xy=xy[0], xytext=xytext[0],
                     horizontalalignment='center', verticalalignment='center', fontsize=5)
    ax.set_title('The Number of '+variable_name+' in Washington', fontdict={
                 'fontsize': '16', 'fontweight': '1'})
    plt.savefig(variable_name+'.png')