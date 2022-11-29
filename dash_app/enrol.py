from dash import html
import dash_bootstrap_components as dbc



name_input = html.Div(
    [
        dbc.Label("Name", html_for="customer_name"),
        dbc.Input(type="text", id="customer_name", placeholder="Enter customer name"),
    ],
    className="mb-3")

address_input = html.Div(
    [
        dbc.Label("Address", html_for="form_address"),
        dbc.Input(type="text", id="form_address", placeholder="Enter customer address"),
    ],
    className="mb-3")

phone_input = html.Div(
    [
        dbc.Label("Phone No.", html_for="form_phone"),
        dbc.Input(type="tel", id="form_phone", placeholder="Enter customer phone no."),
    ],
    className="mb-3")

nin_input = html.Div(
    [
        dbc.Label("Product ID.", html_for="form_nin"),
        dbc.Input(type="number", id="form_nin", placeholder="Enter Product ID.")
    ],
    className="mb-3")

coordinates_input = html.Div(
    [
        dbc.Row([
            dbc.Label("Latitude", html_for="form_lat"),
            dbc.Col([dbc.Input(type="number", id="form_lat", placeholder="Enter latitude", disabled=False)]),
            dbc.Label("Longitude", html_for="form_lon"),
            dbc.Col([dbc.Input(type="number", id="form_lon", placeholder="Enter longitude", disabled=False)])
        ], class_name="row")
    ],
    className="mb-3")

form = dbc.Form([
    html.H3('Product Registration Form', className='text-center'),
    name_input, address_input, phone_input, nin_input, coordinates_input,
    html.Br(),
    html.Br(),
    dbc.Col(dbc.Button(id='enrol_button', children='Submit', class_name='search_btn'), class_name='d-flex justify-content-center'),
    html.Br(),
    dbc.Col(dbc.Alert(id='enrolment_alert', fade=True, color='success', duration=3000, is_open=False)),
    html.Br(),
], id='enrol_form')


style_1 = {
#     "background": "rgba(255,255,255,0.5)",
#    " -webkit-backdrop-filter": 'blur(10px)',
#    ' backdrop-filter':' blur(10px)',
#    ' border': '1px solid rgba(255,255,255,0.25)'
}

form_layout = dbc.Container([
    dbc.Col(form, class_name='col-sm-10 col-lg-8 p-4 container-shadow glassmorph', style=style_1),
], class_name='my-4 py-4 rounded d-flex justify-content-center')