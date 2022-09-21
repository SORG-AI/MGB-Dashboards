# Read Required Libraries
import os
import sys

from flask import Flask
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import random
import plotly.graph_objects as go
from plotly.subplots import make_subplots

## Models Libraries
import datetime
import numpy as np
from codes.util_images import im_preprocess
import cv2
import base64
import pickle

from codes.create_graphs import create_current_graphs, pat_glance_info


#### FIXUS BEGINS
PATHS = {
    'images': os.path.join('images'),
    'app_data' : os.path.join('data','app_data'),
    'data_aaos' : os.path.join('data','aaos_database')
    }

### Loading Data for MGB Dashboard
file_name = os.path.join(PATHS['app_data'], 'AJRR_General_2021Q1-2021Q4_app_data.pkl')
fileo = open(file_name,'rb')
df = pickle.load(fileo)


#try creating surgeon list here
surgeons = df.SurFirstName.astype(str) + ' ' +df.SurLastName.astype(str)
surgeons = surgeons.drop_duplicates()

#create username for each primary surgeon using a loop
USER_TO_NAME = {}
USER_LIST= {}

for x in surgeons:
    un = []
    if type(x) == str:
        for i in range(len(surgeons)): 
            un = x[0] + x.rsplit(' ', 1)[1]
            USER_TO_NAME.update({str(un) : x})
            USER_LIST.update({str(un): (x[0: 2] + x[0:2])})
print(USER_LIST)

# CREDIT: This code follows the template here:
# https://dash.plotly.com/urls

# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
# Exposing the Flask Server to enable configuring it for logging in
server = Flask(__name__)
app = dash.Dash(__name__, server=server,
                title='Fixus App v0.0.1',
                update_title='Cooking awesomeness...',
                suppress_callback_exceptions=True)

# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
#server.config.update(SECRET_KEY=os.getenv('SECRET_KEY'))
server.secret_key = "Velam Kon!"#os.urandom(24)
#server.config.update(SECRET_KEY=os.urandom(24))

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# User data model. It has to have at least self.id as a minimum
class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    ''' This function loads the user by user id. Typically this looks up the user from a user database.
        We won't be registering or looking up users in this example, since we'll just login using LDAP server.
        So we'll simply return a User object with the passed in username.
    '''
    return User(username)


#### User status management views
# Login screen
login = html.Div([dcc.Location(id='url_login', refresh=True),
                  html.H2('''Welcome to FIXUS!''', id='h1'),
                  html.H2('''Please log in to continue:''', id='h2'),
                  dcc.Input(placeholder='Enter your username',
                            type='text', id='uname-box'),
                  html.Br(),                  
                  html.Br(),
                  dcc.Input(placeholder='Enter your password',
                            type='password', id='pwd-box'),
                  html.Br(),
                  html.Br(),
                  html.Br(),
                  html.Button(children='LOGIN', n_clicks=0, style={'backgroundColor': '#00BFFF', 'border-color': '#F5FFFA', 'color' : '#F5FFFA', 'font-size': '20px', 'padding': '10px 25px'},
                              type='submit', id='login-button'),
                  html.Div(children='', id='output-state'),
                  html.Br(),
                  dcc.Link('Home', href='/')], 
                  style={'backgroundColor': 'rgb(220, 248, 285)', 'display': 'inline-block','width':'100%', 'text-align': 'center'})
# Successful login screen
success = html.Div([html.Div([html.H2('Login successful.'),
                              html.Br(),
                              dcc.Link('Home', href='/')], style={'backgroundColor': 'rgb(220, 248, 285)', 'display': 'inline-block','width':'100%'})  # end div
                    ], 
                   style={'backgroundColor': 'rgb(220, 248, 285)', 'display': 'inline-block','width':'100%', 'text-align': 'center'})  # end div
# Failed Login
failed = html.Div([html.Div([html.H2('Log in Failed. Please try again.'),
                             html.Br(),
                             html.Div([login]),
                             dcc.Link('Home', href='/')
                             ])  # end div
                   ])  # end div
# Logout screen
logout = html.Div([html.Div(html.H2('You are securely logged out - Please login to access your data!')),
                   html.Br(),
                   dcc.Link('Home', href='/')
                   ], style={'backgroundColor': 'rgb(220, 248, 285)', 'display': 'inline-block','width':'100%'})  # end div



@app.callback(
    Output('url_login', 'pathname'), Output('output-state', 'children'), [Input('login-button', 'n_clicks')], [State('uname-box', 'value'), State('pwd-box', 'value')])
def login_button_click(n_clicks, username, password):
    
    # we need this to account for empty pass code
    password = '' if password == None else password
    
    # Check the pass and go to the next page
    if n_clicks > 0:
        try:
            if username in USER_LIST.keys() and password == USER_LIST[username]:
                user = User(username)
                login_user(user)
                return '/success', ''
        except:
            return '/login', 'Incorrect username or password'
    else:
        return '/login', ''


# Main Layout
post_login_content = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='redirect', refresh=True),
    dcc.Store(id='login-status', storage_type='session'),
    html.Div(id='user-status-div'),
    html.Div(id='show-output', children='username', style ={'textAlign': 'right'}),
    html.P(id = 'surgeon-name', children = 'name', style ={'textAlign': 'right'}),
    html.Hr(),
    html.Br(),
    html.Div(id='page-content'),
])

app.layout = post_login_content


#####src= os.path.join(PATHS['images'], 'sorglogo.png')
index_page = html.Div([
    html.H1('Fixus - ASR Cervical Spine', style={'font-family' : 'cursive','padding' : '0px 30px', 'font-size' : '60px', 'text-decoration': 'bold', 'font-style': 'oblique',
                       'font-variant': 'small-caps', 'font-stretch': 'ultra-expanded', 'text-align':'center'}),
    html.H1('MAIN MENU', style={'font-family' : 'Helvetica', 'font-size' : '20px', 'text-decoration': 'bold', 'padding': '0px 30px',
                                'backgroundColor': 'rgb(220, 248, 285)', 'text-align': 'center'}),
    html.Div([
        dcc.Link('MGB Dashboard', href='/page-1', style={'font-family' : 'Helvetica', 'font-size' : '15px', 'text-decoration': 'bold', 'text-align':'center', 'padding' : '30px 10px'}),
        html.Br()
        ], style ={'border-top': '1px gray solid', 'border-bottom': '1px gray solid', 'justify-content':'center', 'display': 'flex'}),
    html.Img(src = 'https://i1.wp.com/onlyvectorbackgrounds.com/wp-content/uploads/2019/03/Subtle-Lines-Abstract-Gradient-Background-Cool.jpg?fit=1191%2C843', width = '100%', height='400px')
], style={ 'width':'100%'})



# the whole blue row on the dashboard that gives patient info at a glance

pat_info_at_glance =  html.Div([

                            html.H4(children ='Patient Information At A Glance', style={'text-align': 'center'}),

                            html.Div([

                                dbc.Card([

                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Total patients'], className = 'card-title',

                                                        style ={'textAlign': 'center','color': '#0074D9'}),

                                                html.P(id = 'num_patients', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                            ])

                                    ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                ], style={'display': 'inline-block', 'padding':'10px, 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Institution', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(id = 'inst', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average patient age', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(id = 'avgAge', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Sex Ratio', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(id = 'sex_ratio', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average patient BMI', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(id = 'avgBMI', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average hospitalization duration', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(id = 'avg_stay', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),
                            
                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average CCI', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(id = 'med_CCI', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block'}),
                            
                            
                            html.Div([

                                    html.H4('', className= 'card-title',

                                                style={'textAlign': 'center','color': '#0074D9'}),

                                    html.P('', className='card-content',

                                               style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                              ],  style={'backgroundColor': 'rgb(220, 248, 285)'})

                            ], style={'backgroundColor': 'rgb(220, 248, 285)'})


pat_info_header = html.Div([

                              html.Div([

                                      html.H2([

                                          "Patient Related Data"

                                              ])

                                      ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                              ], style={'backgroundColor': 'rgb(220, 248, 285)', 'display': 'inline-block','width':'100%'})


surg_info_header = html.Div([

                              html.Div([

                                      html.H2([

                                          "Surgeon Related Data"

                                              ])

                                      ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                              ], style={'backgroundColor': 'rgb(220, 248, 285)', 'display': 'inline-block','width':'100%'})


## Procedures and conditions

proc_info = html.Div([

                        html.Div([

                                html.H5([

                                        "Procedures and condition related information"

                                        ])

                                ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                        ], style={'backgroundColor': 'rgb(224, 224, 255)', 'display': 'inline-block', 'width': '100%'})


proc_total = html.Div([

                 html.Div([

                          dcc.Graph(id = 'proc_distr_pie')

                          ], style={'width': '100%','display': 'inline-block'})

                ])

### DROPDOWNS

provider_dropdown = dcc.Dropdown(
    options=[{'label': 'All MGB Data', 'value': 'All'},
             {'label': 'My Data', 'value': 'Surgeon'}], 
    value='All', 
    id='provider_dd')

diag_dropdown = dcc.Dropdown(id='diag_dd')

inst_dropdown = dcc.Dropdown(id='inst_dd')

filter_dropdowns = html.Div([
    html.Div([provider_dropdown], style={'width':'33%','display':'inline-block'}),
    html.Div([inst_dropdown], style={'width':'33%','display':'inline-block'}),
    html.Div([diag_dropdown], style={'width':'33%','display':'inline-block'})
    ])


#####THIS IS THE MAIN DASHBOARD PAGE LAYOUT: please don't clutter

page_1_layout = html.Div([

            dcc.Link('Go back to home', href='/'),
            
            html.Div([

                html.H3("Analytics Dashboard")], style={'textAlign': 'center'}),
            
                dcc.Tab(label = 'MGB Patients', children = [
                                                          filter_dropdowns,
                                                          
                                                          html.Br(),
                    
                                                          pat_info_at_glance,
                                                                                                                        
                                                          html.Br(),
                                                          
                                                          surg_info_header,
    
                                                          proc_info,
    
                                                          proc_total
                                                          
                                                        ])
                       
])





############################## USER STATUS
@app.callback(Output('user-status-div', 'children'), 
              Output('login-status', 'data'), 
              [Input('url', 'pathname')])
def login_status(url):
    ''' callback to display login/logout link in the header '''
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated \
            and url != '/logout':  # If the URL is /logout, then the user is about to be logged out anyways
        return dcc.Link('logout', href='/logout'), current_user.get_id()
    else:
        return dcc.Link('login', href='/login'), 'loggedout'


#Displaying username
@app.callback(
    Output(component_id='show-output', component_property='children'),
    Output(component_id = 'surgeon-name', component_property='children'),
    [Input('login-status','data')])
def update_output_div(username):
    if username in USER_TO_NAME.keys():
        try: 
            name = USER_TO_NAME[username]            
            return ('Username: {}'.format(username), 'Name: {}'.format(name))
        except:  
            return ('','No Surgeon Specific Data')
    else:
        return ('', '')
    
#Set diagnosis dropdown options
@app.callback(
    Output('inst_dd','options'),
    Output('diag_dd', 'options'),
    Input('login-status','data'),
    Input('provider_dd', 'value')
    )
def set_diag_dd_option(username, value):
    if value == 'Surgeon':
        #USER_TO_NAME mapped to surgeon first and last name
        sur_first_last = USER_TO_NAME[username].rsplit(' ',1)
        cond1 = df.SurFirstName == sur_first_last[0]
        cond2 = df.SurLastName == sur_first_last[1]
        data = df.loc[cond1 & cond2]
    else:
        data = df
    
    #setting institution dropdown options
    inst_dd_options = [{'label': i, 'value': i} for i in data.Hosp_name.unique()]
    
    #setting diagnosis dropdown options
    main_diag = data.DX_Main_Category.unique()
    diag_dd_options = [{'label': i, 'value': i} for i in main_diag]
    
    return (inst_dd_options, diag_dd_options)

#Set institution dropdown values based on options
@app.callback(
    Output('inst_dd','value'),
    Input('inst_dd','options')
    )
def set_inst_dd_value(available_options):
    return available_options[0]['value']

#Set diagnosis dropdown value based on options
@app.callback(
    Output('diag_dd', 'value'),
    Input('diag_dd', 'options')
    )
def set_diag_dd_value(available_options):
    return available_options[0]['value']


#Patient info at a glance
@app.callback(
    Output('num_patients','children'), 
    Output('sex_ratio','children'),
    Output('avg_stay', 'children'),
    Output('avgBMI', 'children'),
    Output('avgAge', 'children'),
    Output('med_CCI', 'children'),
    Output('inst', 'children'),
    Input('login-status','data'),
    Input('provider_dd','value'),
    Input('inst_dd','value'),
    Input('diag_dd','value'))
def update_pat_info(username, provider, inst, diag):
    if username in USER_TO_NAME.keys():
        try: 
            if provider == 'Surgeon':
                #USER_TO_NAME mapped to surgeon first and last name
                sur_first_last = USER_TO_NAME[username].rsplit(' ',1)
                cond1 = df.SurFirstName == sur_first_last[0]
                cond2 = df.SurLastName == sur_first_last[1]
                data = df.loc[cond1 & cond2]
            else:
                data = df
            
            data = data[data.Hosp_name == inst]
            data = data[data.DX_Main_Category == diag]
            
            (AJRRPat_total, males_ratio, female_ratio, avg_length_of_stay, avg_BMI, avg_pat_age, med_CCI, inst) = pat_glance_info(data)

            AJRRPat_total_output = '{}'.format(AJRRPat_total)
            sex_ratio_output = '{}% male and {}% female'.format(males_ratio, female_ratio)           
            avg_stay_output = '{}'.format(avg_length_of_stay)
            avg_BMI_output = '{}'.format(avg_BMI)
            avg_age_output = '{}'.format(avg_pat_age)
            med_CCI_output = '{}'.format(med_CCI)
            inst_output = '{}'.format(inst)
            
            return (AJRRPat_total_output, sex_ratio_output, avg_stay_output, avg_BMI_output, avg_age_output, med_CCI_output, inst_output)
        except:  
            return ('', '','', '', '','','')
    else:
        return ('','','', '', '', '', '')


#Charts and graphs
@app.callback(
    Output('proc_distr_pie','figure'),
    Input('login-status','data'),
    Input('provider_dd' ,'value'),
    Input('inst_dd','value'),
    Input('diag_dd','value'))
def update_sur_spec_info(username, provider, inst, diag):

    if username in USER_TO_NAME.keys():
        try:
            if provider == 'Surgeon':
                #USER_TO_NAME mapped to surgeon first and last name
                sur_first_last = USER_TO_NAME[username].rsplit(' ',1)
                cond1 = df.SurFirstName == sur_first_last[0]
                cond2 = df.SurLastName == sur_first_last[1]
                data = df.loc[cond1 & cond2]
            else:
                data = df
                
            data = data[data.Hosp_name == inst]
            data = data[data.DX_Main_Category == diag]
            
            (proc_distr_pie) = create_current_graphs(data)
        
            return (proc_distr_pie)
        
        except:
            return ('')
    else:
        return ('')
        

# Main router
@app.callback(Output('page-content', 'children'), Output('redirect', 'pathname'),
              [Input('url', 'pathname')])
def display_page(pathname):
    ''' callback to determine layout to return '''
    # We need to determine two things for everytime the user navigates:
    # Can they access this page? If so, we just return the view
    # Otherwise, if they need to be authenticated first, we need to redirect them to the login page
    # So we have two outputs, the first is which view we'll return
    # The second one is a redirection to another page is needed
    # In most cases, we won't need to redirect. Instead of having to return two variables everytime in the if statement
    # We setup the defaults at the beginning, with redirect to dash.no_update; which simply means, just keep the requested url
    view = None
    url = dash.no_update
    if pathname == '/login':
        view = login
    elif pathname == '/success':
        if current_user.is_authenticated:
            view = success
        else:
            view = failed
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            view = logout
        else:
            view = login
            url = '/login'

    elif pathname == '/page-1':
        if current_user.is_authenticated:
            view = page_1_layout
        else:
            view = 'Redirecting to login...'
            url = '/login'         
    else:
        view = index_page
    # You could also return a 404 "URL not found" page here
    return view, url


# "complete" layout
app.validation_layout = html.Div([
    login,
    success,
    failed,
    logout,
    post_login_content,
    page_1_layout,
])



if __name__ == '__main__':
    app.run_server(debug=True)