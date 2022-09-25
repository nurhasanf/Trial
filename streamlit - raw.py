import geemap.foliumap as geemap
import main as st
import folium
import ee
from algorithms.lst_PSC import LandsatLSTretrieval
import pandas as pd
import plotly.express as px

# ee.Initialize()

st.set_page_config(layout='wide')
st.title('Interactive Map')
col1,col2 = st.columns([4,1])
with col2:
    option = ('ROADMAP','SATELLITE','TERRAIN','Esri.WorldImagery')
    add_select = st.sidebar.selectbox('Choose Basemap!', option, index=0)
    st.subheader('Search by coordinate')
    with st.form(key='coordinate'):
        Latitude = st.text_input('Latitude', value=0)
        Longitude = st.text_input('Longitude', value=0)
        submit = st.form_submit_button('Submit')
        # st.session_state.Latitude = Latitude
        # st.session_state.Longitude = Longitude


if submit:
    st.subheader('Tabel hasil dari ekstraksi sampel data')
    coordinate = ee.Geometry.Point(float(Longitude), float(Latitude))
    dataset = LandsatLSTretrieval('L8', '2013-01-01', '2023-01-01', coordinate)

    sample = dataset.select(['AWVhour','NDVI','Emissivity','FVC','LST']).getRegion(coordinate, 30).getInfo()

    df = pd.DataFrame(sample)
    colname = df.iloc[0]
    df = pd.DataFrame(sample[1:], columns=colname)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.dropna()

    st.dataframe(df)
    stats = df[['AWVhour','NDVI','Emissivity','FVC','LST']].describe()
    st.dataframe(stats)
    plot = px.line(x=df['time'],y=df['LST'])
    scatter = px.scatter(df[['NDVI','LST']], y='NDVI', x='LST')
    st.write(plot)
    st.write(scatter)
# with col2:
#     option = dataset.first().bandNames().getInfo()
#     empty = st.empty()
#     band = empty.multiselect('choose Band', option)




# Select basemap
# option = ('ROADMAP','SATELLITE','TERRAIN','Esri.WorldImagery')
# add_select = st.sidebar.selectbox('Choose Basemap!', option, index=0)

with col1:
    Map = geemap.Map(
        Draw_export=True,
        location=[-6.7210, 108.5575],
        zoom_start=11,
        plugin_LatLngPopup=True,
        basemap=add_select)

    # lat = float(st.session_state.get('Latitude'))
    # lon = float(st.session_state.get('Longitude'))

    if submit:
        Map.add_marker(location=[Latitude,Longitude])
        # Map.addLayer(dataset.sort('CLOUD_COVER').first().select('LST'), {'min': 20 , 'max': 45, 'palette': ['blue','green', 'yellow', 'red']}, 'LST')
        Map.centerObject(coordinate, zoom=11)    
    Map.to_streamlit(height=480)




# Map.addLayer(image, image_viz_params, 'NIR', False)
# Map.addLayer(landSurfaceTemperature, landSurfaceTemperatureVis,'Land Surface Temperature', False)











