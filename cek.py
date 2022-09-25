import geemap.foliumap as geemap
from datetime import date
import streamlit as st
import ee
from algorithms.lst_SMW import collection
import pandas as pd
import plotly.express as px

# ee.Initialize()

## Conversion Functions
def toCelcius(image):
    thermal = image.select('LST').subtract(273.15)
    return image.addBands(thermal, None, True)


# get landsat collection with added variables: NDVI, FVC, TPW, EM, LST
def load_dataset():
    satellite = 'L8'
    date_start = '2013-01-01'
    date_end = str(date.today())
    site = ee.Geometry.Point([108.550659,-6.737246])
    geometry = site.buffer(30)
    use_ndvi = True
    LandsatColl = collection(satellite, date_start, date_end, geometry, use_ndvi) \
                  .sort('CLOUD_COVER') \
                  .first()


    return LandsatColl

# st.write(load_dataset().getInfo())

cmap1 = ['blue', 'cyan', 'green', 'yellow', 'red']
cmap2 = ['F2F2F2','EFC2B3','ECB176','E9BD3A','E6E600','63C600','00A600']

Map = geemap.Map()
Map.addLayer(load_dataset().select('LST'), {'min': 20 , 'max': 45, 'palette': ['blue', 'yellow','red']}, 'LST')
Map.addLayer(load_dataset().select('FVC'),{'min':0.0, 'max':1.0, 'palette':cmap2}, 'FVC')
Map.addLayer(load_dataset().select('EM'),{'min':0.9, 'max':1.0, 'palette':cmap1},'EM')
Map.addLayer(load_dataset().select(['SR_B4','SR_B3','SR_B2']), {'min':0, 'max':0.3}, 'RGB')
Map.addLayer(load_dataset().select('NDVI'), {'min':-1, 'max':1, 'palette':cmap2}, 'NDVI')
Map.to_streamlit()