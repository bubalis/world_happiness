# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 14:00:31 2019

@author: benja
"""

#!/usr/bin/env python
# coding: utf-8

# In[17]:


import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import fiona
import requests
import json
from bokeh.io import output_notebook, show, output_file, curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar,  HoverTool, Panel
from bokeh.palettes import brewer
from bokeh.layouts import WidgetBox, row
from bokeh.models.widgets import  RadioGroup
from bokeh.models.annotations import Title
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


labels=['Life Satisfaction',
 'Log GDP per capita',
 'Social support',
 'Healthy life expectancy at birth',
 'Positive Affect: % of time spent happy',
 'Negative Affect: % of time feeling negative emotions',
 'Confidence in national government',
 'Gini Index: Income Inequality']

    

df=pd.read_csv('https://github.com/bubalis/world_happiness/blob/master/modified_dataset.csv?raw=true')

merged = gdf.merge(df, left_on = 'country', right_on = 'country', how='inner')
merged= merged.append(gdf[gdf['country'].isin( merged['country'].unique())==False])
merged.fillna('No Data', inplace=True)

# In[143]:


def make_dataset(indicator, df):
    df['indicator_to_display']=df[indicator]
    df_json = json.loads(df.to_json())
    #Convert to String like object.
    json_data = json.dumps(df_json)
    #Input GeoJSON source that contains features for plotting.
    #geosource = GeoJSONDataSource(geojson = json_data)
    return json_data

def make_plot(geosource, indicator):
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
    border_line_color=None,location = (0,0), orientation = 'horizontal')
    #Create figure object.
    p = figure( plot_height = 600 , plot_width = 850, 
               toolbar_location = 'left', tools=[hover])
    p.title=t
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    #Add patch renderer to figure. 
    p.patches('xs','ys', source = geosource, fill_color = {'field' :'indicator_to_display', 'transform' : color_mapper},
              line_color = 'black', line_width = 0.25, fill_alpha = 1)
    #Specify figure layout.
    p.add_layout(color_bar, 'below')

    return p




def is_int(x):
    try:
        int(x)
        return True
    except: 
        return False


def update_plot(attr, old, new):
    i=indicator_selector.active
    indicator=labels[i]
    new_data=make_dataset(indicator, merged)
    geosource.geojson = new_data
    vals=merged[merged[indicator].apply(is_int)][indicator]
    minimum=vals.min()
    maximum=vals.max() 
    if indicator in ['Negative Affect: % of time feeling negative emotions', 'Gini Index: Income Inequality']:
        color_mapper.update(low = minimum, high = maximum, palette=palette[::-1])
    else:
        color_mapper.update(low = minimum, high = maximum, palette=palette)
    t.text=indicator
    
        
#%%
hovertext=[('Country:', '@country')]+[(f'{label}:', '@{'+label+'}') for label in labels]

indicator_selector=RadioGroup(labels=labels, active=0)
indicator_selector.on_change('active', update_plot)
indicator='Life Satisfaction'
json_data=make_dataset(indicator, merged)
geosource = GeoJSONDataSource(geojson = json_data)
palette = brewer['RdYlGn'][8][::-1]
t=Title()
t.text=indicator
hover = HoverTool(tooltips = hovertext
                )
color_mapper = LinearColorMapper(palette = palette, low = 3, high = 8, nan_color = 'grey')
p=make_plot(geosource, indicator)
controls = WidgetBox(indicator_selector , height=60, width=320)
l = row(controls, p)
curdoc().add_root(l)
show(l)
