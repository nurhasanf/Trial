import streamlit as st
import numpy as np
import ee
import geemap.foliumap as geemap
import pandas as pd

# ee.Initialize()

st.set_page_config(layout='wide')

site = ee.Geometry.Point([108.5078, -6.7505])
geometry = site.buffer(30)
start_date = '2013-01-01'
end_date = pd.to_datetime('today').strftime('%Y-%m-%d')


from tempfile import NamedTemporaryFile
from PIL import Image

input = st.file_uploader('Upload AOI *.shp file', type=['tif'])

if input :
   with NamedTemporaryFile('wb',suffix='.tif') as f:
    f.write(input.getvalue())
    im = Image.open(f.name)


# dataset = ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA") \
#             .filterDate(start_date, end_date) \
#             .filterBounds(geometry) \

# scene_id = dataset.aggregate_array('system:index')
# options = scene_id.getInfo()

# with st.sidebar:
#     with st.expander('Layer Options'):
#         st.markdown(' ')
#         basemap_list = ['ROADMAP','SATELLITE','TERRAIN','Esri.WorldImagery']
#         st.selectbox('Choose Basemap!', options=basemap_list, index=0, key='basemaps')
#         st.selectbox(label='Select Scene', options=options, key='sceneId')
#     with st.expander('Band Options'):
#         st.markdown(' ')  
#         # Composite Band
#         composite_container = st.container()
#         composite_all = st.checkbox('All composite')
#         composite_options = ['TrueColor', 'FalseColor', 'ColorInfrared',
#                             'Agriculture', 'AtmosphericPenetration', 'HealthlyVegetation',
#                             'Land/Water', 'NaturalWithAtmosphericRemoval', 'ShortwaveInfrared',
#                             'VegetationAnalysis']

#         if composite_all:
#             composite_container.multiselect(
#                         label = 'Band Composite',
#                         options = composite_options,
#                         default = composite_options,
#                         key = 'composite')

#         else:
#             composite_container.multiselect(
#                         label = 'Band Composite',
#                         options = composite_options,
#                         key = 'composite')
        
#         # Band Ratio
#         ratio_container = st.container()
#         ratio_all = st.checkbox('All band')
#         ratio_options = ['NDVI','NDBI','NDWI']

#         if ratio_all:
#             ratio_container.multiselect(
#                         label = 'Band Ratio', 
#                         options = ratio_options, 
#                         default = ratio_options, 
#                         key = 'ratio')

#         else:
#             ratio_container.multiselect(
#                         label = 'Band Ratio', 
#                         options = ratio_options, 
#                         key = 'ratio')
        

# composite = st.session_state['composite']
# bands = []

# for item in composite:
#     if item == 'TrueColor':
#         bands.append({'TrueColor':['B4','B3','B2']})
#     elif item == 'FalseColor':
#         bands.append({'FalseColor':['B7','B6','B4']})
#     elif item == 'ColorInfrared':
#         bands.append({'ColorInfrared':['B5','B4','B3']})
#     elif item == 'Agriculture':
#         bands.append({'Agriculture':['B6','B5','B2']})
#     elif item == 'AtmosphericPenetration':
#         bands.append({'AtmosphericPenetration':['B7','B6','B5']})
#     elif item == 'HealthlyVegetation':
#         bands.append({'HealthlyVegetation':['B5','B6','B2']})
#     elif item == 'Land/Water':
#         bands.append({'Land/Water':['B5','B6','B4']})
#     elif item == 'NaturalWithAtmosphericRemoval':
#         bands.append({'NaturalWithAtmosphericRemoval':['B7','B5','B3']})
#     elif item == 'ShortwaveInfrared':
#         bands.append({'ShortwaveInfrared':['B7','B5','B4']})
#     elif item == 'VegetationAnalysis':
#         bands.append({'VegetationAnalysis':['B6','B5','B4']})

# Map = geemap.Map(
#     Draw_export=True,
#     location=[-6.8392, 107.6440],
#     zoom_start=8,
#     plugin_LatLngPopup=True
#     )

# @st.experimental_memo(show_spinner=False)
# def layer(Basemap, scene_id, bands):
#     data = dataset.filter(ee.Filter.eq('system:index', scene_id)) \
#                   .first()

#     Map.add_basemap(basemap=Basemap)

#     for dict in bands:
#         for key,value in dict.items():
#             Map.addLayer(data, {'min':0,'max':0.3,'bands':value}, key, False)


#     Map.to_streamlit(height=480)

# layer(st.session_state['basemaps'], st.session_state['sceneId'], bands)
