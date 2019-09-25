# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 14:09:00 2019

@author: benja
"""

import pandas as pd
import geopandas as gpd
import fiona
import requests
import numpy as np
# In[18]:


df=pd.read_csv('https://github.com/bubalis/world_happiness/blob/master/Chapter2OnlineData.csv?raw=true')



def intmaker(string):
    string=str(string)
    try:
        return int(string.replace(',',''))
    except:
        return None
def unpack_shpfile(url):
    url=url+'?raw=true'
    request = requests.get(url)
    b = bytes(request.content)
    with fiona.BytesCollection(b) as f:
        crs = f.crs
        gdf = gpd.GeoDataFrame.from_features(f, crs=crs)
        return gdf

# In[24]:


url='https://github.com/bubalis/world_happiness/blob/master/ne_110m_admin_0_countries.zip'

gdf = unpack_shpfile(url)
#Read shapefile using Geopandas


gdf = gdf[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']


country_corrections={'United States': 'United States of America',
                     'Taiwan Province of China':'Taiwan', 
 'Congo (Brazzaville)' :  'Republic of the Congo',
 'Congo (Kinshasa)':  'Democratic Republic of the Congo',
 'Czech Republic': 'Czechia',
 'Palestinian Territories': 'Palestine',
 'North Cyprus': 'Northern Cyprus',
 'Serbia' : 'Republic of Serbia',
 'Somaliland region': 'Somaliland',
 'Swaziland': 'eSwatini',
 'Tanzania': 'Tanzania',
                     
                     }

df=df.rename(columns={'Life Ladder': 'Life Satisfaction',
                              'Positive affect': 'Positive Affect: % of time spent happy', 
                              'Negative affect': 'Negative Affect: % of time feeling negative emotions',
                               'GINI index (World Bank estimate), average 2000-16': 'Gini Index: Income Inequality'})
labels=['Life Satisfaction',
 'Log GDP per capita',
 'Social support',
 'Healthy life expectancy at birth',
 'Positive Affect: % of time spent happy',
 'Negative Affect: % of time feeling negative emotions',
 'Confidence in national government',
 'Gini Index: Income Inequality']

def country_correct(string): ###Align Country names between data sources
    if string in gdf['country'].tolist():
        return string
    else:
        return country_corrections.get(string)
    


def latest_valid(df): #find newest valid entry for statistic
    results=[]
    #print(labels)      
    for country in df['Country2'].unique():
        dictionary={'country': country}
        for indicator in labels:
            for year in range(2018, 2005, -1):
                #print('anything')
                try:
                    row= df[(df['Country2']==country) & (df['Year']==year)].iloc[0]
                #print (row)
                except:
                    continue
                if type(row[indicator])==np.float64:
                    dictionary[indicator]=row[indicator]
                    dictionary[f'{indicator} latest year']=year
                    break
                

        results.append(dictionary)
    return results

df["Country2"]=df['Country name'].apply(country_correct)
df= pd.DataFrame(latest_valid(df))
df.to_csv(r'C:\Users\benja\Documents\Outside_teaching\charts\happiness_Indicators\modified_dataset.csv')