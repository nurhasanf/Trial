import geemap.foliumap as geemap
from datetime import date
import streamlit as st
import ee
from algorithms.lst_PSC import LandsatLSTretrieval
import pandas as pd
import plotly.express as px
import altair as alt
import json

st.set_page_config(layout='wide')

json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]

@st.experimental_memo
def Initialize():
    # Preparing values
    json_object = json.loads(json_data, strict=False)
    service_account = json_object['client_email']
    json_object = json.dumps(json_object)
    # Authorising the app
    credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
    ee.Initialize(credentials)

Initialize()

# @st.experimental_memo
# def Initialize():
#     ee.Initialize()

# Initialize()


st.title('Interactive Map')

col1, col2 = st.columns([4,1])
with col2:
    st.subheader('Search by coordinate')
    with st.form(key='coordinate'):
        st.text_input('Latitude', value=0, key='lat')
        st.text_input('Longitude', value=0, key='lon')
        submit = st.form_submit_button('Submit')

lat = float(st.session_state['lat'])
lon = float(st.session_state['lon'])

def load_dataset(**kwargs):
    kwargs['Latitude'] = lat
    kwargs['Longitude'] = lon
    site = ee.Geometry.Point([kwargs['Longitude'], kwargs['Latitude']])
    geometry = site.buffer(30)
    dataset = LandsatLSTretrieval('L8', '2013-01-01', str(date.today()), geometry)
    return dataset

dataset = load_dataset(Latitude=lat, Longitude=lon)
scene_id = dataset.aggregate_array('system:index')
options = scene_id.getInfo()

with st.sidebar:
    with st.expander('Layer Options'):
        st.markdown(' ')
        basemap_list = ['ROADMAP','SATELLITE','TERRAIN','Esri.WorldImagery']
        st.selectbox('Choose Basemap!', options=basemap_list, index=0, key='basemaps')
        st.selectbox(label='Select Scene', options=options, key='sceneId')

@st.experimental_memo       
def load_dataframe(**kwargs):
    kwargs['Latitude'] = lat
    kwargs['Longitude'] = lon
    site = ee.Geometry.Point([kwargs['Longitude'], kwargs['Latitude']])
    geometry = site.buffer(30)

    def properties(image):
        date = ee.Date(image.get('system:time_start'))
        ndvi = image.select('NDVI')
        fvc = image.select('FVC')
        em = image.select('Emissivity')
        awv = image.select('AWVhour')
        lst = image.select('LST')
        return ee.Feature(site, {
            'Longitude':ee.Number(site.coordinates().get(0)),
            'Latitude':ee.Number(site.coordinates().get(1)),
            'Id': ee.String(image.get('system:index')),
            'Date':ee.Number(date.format('YYYY-MM-dd')),
            'Time':ee.Number(date.format('k:m:s')),
            'NDVI':ee.Number(ndvi.reduceRegion(ee.Reducer.mean(),geometry,30).get('NDVI')),
            'FVC':ee.Number(fvc.reduceRegion(ee.Reducer.mean(),geometry,30).get('FVC')),
            'Emissivity':ee.Number(em.reduceRegion(ee.Reducer.mean(),geometry,30).get('Emissivity')),
            'WaterVapor':ee.Number(awv.reduceRegion(ee.Reducer.mean(),geometry,30).get('AWVhour')),
            'LST': ee.Number(lst.reduceRegion(ee.Reducer.mean(),geometry,30).get('LST'))
        })

    MyFeatures = ee.FeatureCollection(load_dataset(Latitude=lat, Longitude=lon).map(properties))
    fc_to_df = geemap.ee_to_pandas(MyFeatures)
    df = pd.DataFrame(fc_to_df)
    df = df.loc[:, ['Id','Latitude','Longitude','Date','Time','NDVI','FVC','Emissivity','WaterVapor','LST']]

    return df

if 'showdata' not in st.session_state:
      st.session_state.showdata = False

if submit or st.session_state['showdata']:
    with st.sidebar:
        with st.expander('Band Options'):
            st.markdown(' ')  
            # Composite Band
            composite_container = st.container()
            composite_all = st.checkbox('All composite')
            composite_options = ['TrueColor', 'FalseColor', 'ColorInfrared',
                                'Agriculture', 'AtmosphericPenetration', 'HealthlyVegetation',
                                'Land/Water', 'NaturalWithAtmosphericRemoval', 'ShortwaveInfrared',
                                'VegetationAnalysis']

            if composite_all:
                composite_container.multiselect(
                            label = 'Band Composite',
                            options = composite_options,
                            default = composite_options,
                            key = 'composite')

            else:
                composite_container.multiselect(
                            label = 'Band Composite',
                            options = composite_options,
                            key = 'composite')
            
            # Band Ratio
            ratio_container = st.container()
            ratio_all = st.checkbox('All band')
            ratio_options = ['NDVI','NDBI','NDWI']

            if ratio_all:
                ratio_container.multiselect(
                            label = 'Band Ratio', 
                            options = ratio_options, 
                            default = ratio_options, 
                            key = 'ratio')

            else:
                ratio_container.multiselect(
                            label = 'Band Ratio', 
                            options = ratio_options, 
                            key = 'ratio')
    with st.expander('Show Tables'):
        st.subheader('Data Table')
        dataframe = load_dataframe(Latitude=lat, Longitude=lon)
        dataframe = dataframe.dropna().reset_index(drop=True)
        st.session_state.showdata = True   

        def df_to_csv(dataframe):
            return dataframe.to_csv().encode('utf-8')

        csv = df_to_csv(dataframe)
        st.dataframe(dataframe)
        st.download_button(
            label = 'Download data as CSV',
            data = csv,
            file_name = 'data.csv',
            mime = 'text/csv'
        )

        st.subheader('Descriptive Statistics')
        df_stats = dataframe[['NDVI','FVC','Emissivity','WaterVapor','LST']].describe()
        st.dataframe(df_stats)
    
    with st.expander('Show Charts'):
        st.subheader('Line Chart')  
        # st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        bands = st.radio(label='Select options:', options=['NDVI','FVC','Emissivity','WaterVapor','LST'])
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

        if bands == 'NDVI':
            st.line_chart(data=dataframe, x='Date', y='NDVI')
        elif bands == 'FVC':
            st.line_chart(data=dataframe, x='Date', y='FVC')
        elif bands == 'Emissivity':
            st.line_chart(data=dataframe, x='Date', y='Emissivity')
        elif bands == 'WaterVapor':
            st.line_chart(data=dataframe, x='Date', y='WaterVapor')
        else:
            st.line_chart(data=dataframe, x='Date', y='LST')

        st.subheader('Scatterplot')
        if 'xaxis' not in st.session_state:
            st.session_state.xaxis = 'NDVI'
        if 'yaxis' not in st.session_state:
            st.session_state.yaxis = 'LST'

        scatter = px.scatter(
                data_frame=dataframe,
                x=st.session_state.xaxis,
                y=st.session_state.yaxis
                )

        column1,column2 = st.columns([1,3])

        with column1:
            st.title(' ')
            with st.form(key='scatter'):
                xaxis = st.selectbox(label='Select x-axis', options=['NDVI','FVC','Emissivity','WaterVapor','LST'], key='xaxis')
                yaxis = st.selectbox(label='Select y-axis', options=['NDVI','FVC','Emissivity','WaterVapor','LST'], key='yaxis')
                st.form_submit_button(label='Submit')
            
        with column2:
            st.plotly_chart(scatter, use_container_width=True)

    composite = st.session_state['composite']
    bands = []

    for item in composite:
        if item == 'TrueColor':
            bands.append({'TrueColor':['SR_B4','SR_B3','SR_B2']})
        elif item == 'FalseColor':
            bands.append({'FalseColor':['SR_B7','SR_B6','SR_B4']})
        elif item == 'ColorInfrared':
            bands.append({'ColorInfrared':['SR_B5','SR_B4','SR_B3']})
        elif item == 'Agriculture':
            bands.append({'Agriculture':['SR_B6','SR_B5','SR_B2']})
        elif item == 'AtmosphericPenetration':
            bands.append({'AtmosphericPenetration':['SR_B7','SR_B6','SR_B5']})
        elif item == 'HealthlyVegetation':
            bands.append({'HealthlyVegetation':['SR_B5','SR_B6','SR_B2']})
        elif item == 'Land/Water':
            bands.append({'Land/Water':['SR_B5','SR_B6','SR_B4']})
        elif item == 'NaturalWithAtmosphericRemoval':
            bands.append({'NaturalWithAtmosphericRemoval':['SR_B7','SR_B5','SR_B3']})
        elif item == 'ShortwaveInfrared':
            bands.append({'ShortwaveInfrared':['SR_B7','SR_B5','SR_B4']})
        elif item == 'VegetationAnalysis':
            bands.append({'VegetationAnalysis':['SR_B6','SR_B5','SR_B4']})


with col1:
    Map = geemap.Map(
        Draw_export=True,
        plugin_LatLngPopup=True
        )

    if 'showmap' not in st.session_state:
        st.session_state['showmap'] = False

    if submit or st.session_state['showmap']:
        st.session_state['showmap'] = True

        @st.experimental_memo(show_spinner=False)
        def layer(Basemap, scene_id, bands):
            data = dataset.filter(ee.Filter.eq('system:index', scene_id)) \
                        .first()

            Map.add_basemap(basemap=Basemap)
            Map.add_marker(location=[lat,lon])

            for dict in bands:
                for key,value in dict.items():
                    Map.addLayer(data, {'min':0,'max':0.3,'bands':value}, key, False)

            Map.centerObject(ee.Geometry.Point([lon, lat]), zoom=11)
            Map.to_streamlit(height=480)

        layer(st.session_state['basemaps'], st.session_state['sceneId'], bands)

    else:
        Map.to_streamlit(height=480)
