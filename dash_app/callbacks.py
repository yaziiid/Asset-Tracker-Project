from dash_extensions.enrich import Output, Input, State, ServersideOutput, FileSystemStore
from dash.exceptions import PreventUpdate
from dash_app.home import home_layout
from dash_app.enrol import form_layout
from urllib.parse import unquote
import pandas as pd
import plotly.express as px
from dash_app.records import customer_records
from dash_app.search import search_layout
from sqlalchemy import engine_from_config
import configparser
# from connect_connector import connect_with_connector
# import os

def register_callbacks(app):
    ##### Database Configuration ######
    config = configparser.ConfigParser()
    config.read('local_db.ini')
    hostname = config['HOST_DATA']['hostname']
    username = config['USER_DATA']['username']
    password = config['USER_DATA']['password']
    database = config['USER_DATA']['database']

    # map_api = os.environ['MAPBOX_API']
    map_api = 'pk.eyJ1IjoieWF6aWlkIiwiYSI6ImNsYXI1a2xmczFxOWQzb3RhNWZnODBteTAifQ.tiRSI-AleU_c_m2tHWAP7Q'
    content = ['home', 'register', 'records', 'search']

    fss = FileSystemStore(threshold=5)


    @app.callback(
    ServersideOutput('cached_data', 'data', backend=fss),
    Input('query_data', 'n_intervals')
    , memoize=True)
    def query_data(n):
        config = {'db.url': f'mysql+pymysql://{username}:{password}@{hostname}/{database}'}
        engine = engine_from_config(config, prefix='db.')
        # engine = connect_with_connector()

        df = pd.read_sql_table('customer_profile', engine)
        engine.dispose()
        return df

    @app.callback(
    Output('content_container', 'children'),
    Output('home', 'active'),
    Output('register', 'active'),
    Output('records', 'active'),
    # Output('search', 'active'),
    Input('location', 'pathname')
    )
    def display_content(pathname):
        page = unquote(pathname[1:])
        if page in content:
            if page == 'home':
                return home_layout, True, False, False
            if page == 'register':
                return form_layout, False, True, False
            if page == 'records':
                return customer_records, False, False, True
            # if page == 'search':
            #     return search_layout, False, False, False, True
        else:
            if page != 'logout':
                return home_layout, True, False, False

    
    hovertemplate = ('<b>Name: </b>: %{customdata[1]} <br>' +
                '<b>Address: </b>: %{customdata[2]}<br>' + 
                '<b>Phone No.: </b>: %{customdata[3]}<br>' +
                '<b>Product ID.: </b>: %{customdata[4]}<br>')
    

    @app.callback(
    Output('customer_map', 'figure'),
    Input('home_search', 'value'),
    Input('cached_data', 'data'),
    prevent_initial_call=True
    )
    def plot_map_points(value, data):
        data.dropna(inplace=True)
        if value==None:
            raise PreventUpdate
        if type(value) == str:
            df = data[data['name']==value]
        else:
            df = data[data['nin']==value]
        df = df.iloc[[0]]
        lat = df['latitude'].item()
        lon = df['longitude'].item()
        customer_map = px.scatter_mapbox(
            data, lat='latitude', lon='longitude',
            hover_name='name', custom_data=['id', 'name', 'address', 'phone', 'nin', 'asset_count', 'latitude', 'longitude'],
            hover_data={'name': False, 'latitude':False, 'longitude':False, 'asset_count':True},
            zoom=9, center=dict(lat=lat, lon=lon),
            )
        customer_map.update_traces(marker=dict(size=15, color='#fe6b6b'), hovertemplate = hovertemplate)
        customer_map.update_layout(
            legend =dict(title_text = "", orientation='h', x=0.4, font_size=15, font_color='#FFFFFF'), paper_bgcolor='#E5ECF6',
            margin = dict(l = 0, r = 0, t = 0, b = 0), mapbox_style="streets", mapbox_accesstoken=map_api,
            hoverlabel = dict(bgcolor="#666DE9", font_size=15, font_color='whitesmoke')
        )
        customdata_trace = [df['name'].item(), df['address'].item(), df['phone'].item(), df['nin'].item()]

        hovertemplate_trace = ('<b>Name: ' + customdata_trace[0] + '<br>' +
                    '<b>Address: </b>: ' + customdata_trace[1] + '<br>' + 
                    '<b>Phone No.: </b>: ' + customdata_trace[2] + '<br>' +
                    '<b>Product ID.: </b>: ' + str(customdata_trace[3]) + '<br>')
        customer_map.add_scattermapbox(
            below="", lat=[lat], lon=[lon], customdata=customdata_trace, hovertemplate=hovertemplate_trace,
            showlegend=False, name='',  hoverlabel = dict(bgcolor="#666DE9", font_size=15, font_color='whitesmoke'),
            marker=dict(size = 25, color='#666DE9')
        )


        return customer_map
    

    @app.callback(
    Output('customer_dd', 'options'),
    Output('customer_dd', 'disabled'),
    Output('customer_dd', 'placeholder'),
    Input('search_by', 'value'),
    Input('cached_data', 'data')
    )
    def dropdown_items(value, data):
        labels = {'name': 'Name', 'phone': 'Phone No.', 'nin':'National ID.'}
        if value == None:
            raise PreventUpdate
        options = [{'label':value, 'value':value} for value in data[value].tolist()]
        disabled = False
        placeholder = f'Search by {labels[value]}'


        return options, disabled, placeholder


    @app.callback(
        Output('home_search', 'options'),
        Input('cached_data', 'data')
    )
    def dropdown_items(data):
        names = data['name'].tolist()
        nin = data['nin'].tolist()
        for i in nin:
            names.append(i)
        
        options = [{'label':value, 'value':value} for value in names]


        return options
    

    @app.callback(
    Output('enrolment_alert', 'color'),
    Output('enrolment_alert', 'is_open'),
    Output('enrolment_alert', 'children'),
    Input('enrol_button', 'n_clicks'),
    State('customer_name', 'value'),
    State('form_address', 'value'),
    State('form_phone', 'value'),
    State('form_nin', 'value'),
    State('form_lat', 'value'),
    State('form_lon', 'value'),
    prevent_initial_call=True
    )
    def enrolment_form(n, name, address, phone, nin, lat, lon):
        data = {'name': name, 'address': address, 'phone': phone, 'nin': nin, 'lat': lat, 'lon': lon}
        for i in data.values():
            if not i:
                color = 'danger'
                is_open = True
                msg = 'Please fill all the given fields'
                return color, is_open, msg
        config = {'db.url': f'mysql+pymysql://{username}:{password}@{hostname}/{database}'}
        engine = engine_from_config(config, prefix='db.')
        # engine = connect_with_connector()
        query = "insert into customer_profile (name, address, phone, nin, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s)"
        values = (name, address, phone, nin, lat, lon)
        try:
            with engine.connect() as conn:
                conn.execute(query, values)
            color = 'success'
            is_open = True
            msg = 'Customer enrolled successfully'
        except:
            engine.dispose()
            color = 'success'
            is_open = True
            msg = 'Please enter the correct values on the given fields'
        
        return color, is_open, msg
    

    @app.callback(
    Output('info_markdown', 'children'),
    Input('search_button', 'n_clicks'),
    Input('cached_data', 'data'),
    State('search_by', 'value'),
    State('customer_dd', 'value')
    )
    def customer_info(n, data, by, value):
        if value != None:
            df = data[data[by]==value]
            df = df.iloc[[0]]
            markdown_1 = f'''
                * **Name:** {df['name'].item()}
                * **Address:** {df['address'].item()}
                * **Phone No.:** {df['phone'].item()}
                * **Product ID.: ** {df['nin'].item()}
                * **No of assets in posession: ** {df['asset_count'].item()}
                '''
        else:
            raise PreventUpdate

        return markdown_1
    
    @app.callback(
        Output('customer_table', 'data'),
        Output('customer_table', 'columns'),
        Input('cached_data', 'data')
    )
    def update_records(data):
        data.drop(columns=['id', 'asset_count'], inplace=True)
        data.columns = ['Name', 'Address', 'Phone No.', 'Product ID.', 'Latitude', 'Longitude']
        columns=[{'name':i, 'id':i} for i in data.columns]
        return data.to_dict('records'), columns
