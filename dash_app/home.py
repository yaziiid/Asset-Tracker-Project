from dash import dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import configparser
from sqlalchemy import engine_from_config
import pandas as pd
# from connect_connector import connect_with_connector
# import os


#### Database Configuration ######
config = configparser.ConfigParser()
config.read('cloud_db.ini')
hostname = config['HOST_DATA']['hostname']
username = config['USER_DATA']['username']
password = config['USER_DATA']['password']
database = config['USER_DATA']['database']

#### Connection ####
config = {'db.url': f'mysql+pymysql://{username}:{password}@{hostname}/{database}'}
engine = engine_from_config(config, prefix='db.')
# engine = connect_with_connector()
###### DataFrames #####
customer_profile_df = pd.read_sql_table('customer_profile', engine)
map_api = 'pk.eyJ1IjoieWF6aWlkIiwiYSI6ImNsYXI1a2xmczFxOWQzb3RhNWZnODBteTAifQ.tiRSI-AleU_c_m2tHWAP7Q'
# map_api = os.environ["MAPBOX_API"]
hovertemplate = ('<b>Name: </b>: %{customdata[1]} <br>' +
                '<b>Address: </b>: %{customdata[2]}<br>' + 
                '<b>Phone No.: </b>: %{customdata[3]}<br>' +
                '<b>Product ID.: </b>: %{customdata[4]}<br>')
customer_map = px.scatter_mapbox(
    customer_profile_df, lat='latitude', lon='longitude',
    hover_name='name', custom_data=['id', 'name', 'address', 'phone', 'nin', 'asset_count', 'latitude', 'longitude'],
    hover_data={'name': False, 'latitude':False, 'longitude':False, 'asset_count':True},
    zoom=6, center=dict(lat=9.0765, lon=8),
    mapbox_style = 'carto-positron', height=800, )
customer_map.update_traces(marker=dict(size=15, color='#fe6b6b'), hovertemplate=hovertemplate)
customer_map.update_layout(
    legend =dict(title_text = '', orientation='h', x=0.4, font_size=15, font_color='#FFFFFF'), paper_bgcolor='#E5ECF6',
    margin = dict(l = 0, r = 0, t = 0, b = 0), mapbox_style="streets", mapbox_accesstoken=map_api,
    hoverlabel = dict(bgcolor="#666DE9", font_size=15, font_color='whitesmoke')
)

markdown_1 = f'''
            * **Name:** 
            * **Address:** 
            * **Phone No.:** 
            * **Product ID.: ** 
            * **No of assets in posession: ** 
            '''


home_layout = dbc.Container([
    # dbc.Row([
    #     dbc.Col([
    #         dcc.Dropdown(
    #             id = 'home_search', placeholder= 'search name or product id ', className='dropdown hdd', optionHeight=50,
    #         ),
    #     ], class_name='col-lg-2 mx-auto mb-3')
    # ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=customer_map, id='customer_map', className='card', style={'height': '80vh'}), class_name='map mx-auto col-sm-12 rounded h-auto'),
    ], class_name='align-top')
], fluid=True, class_name='mt-2 mx-0 py-0 px-0 rounded')

engine.dispose()

    