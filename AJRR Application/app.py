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
file_name = os.path.join(PATHS['app_data'], 'AJRR_General_2016Q2-2016Q2_app_data.pkl')
fileo = open(file_name,'rb')
df = pickle.load(fileo)


#try creating surgeon list here
surgeons = df.SurFirstName.astype(str) + ' ' +df.SurLastName.astype(str)
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



# Callback function to login the user, or update the screen if the username or password are incorrect
    #### Creating a dict with all surgeon names and usernames
# list_surgeons = pd.Series(df['surgeons.PrimarySurgeon']).unique().tolist()
# print(list_surgeons)
# #create username for each primary surgeon using a loop

    
# #print(list_surgeons)
# for x in list_surgeons:
#     un = []
#     print(x)
#     if len(str(x)) > 1:
#         for i in range (len(list_surgeons)):
#             un =str(x)[0] + str(x).rsplit(' ', 1)[1]
#             USER_TO_NAME.update({str(un): x})
#             USER_LIST.update({str(un) : str(x[0: 2] + x[0:2])})
    
# print(USER_LIST)

@app.callback(
    Output('url_login', 'pathname'), Output('output-state', 'children'), [Input('login-button', 'n_clicks')], [State('uname-box', 'value'), State('pwd-box', 'value')])
def login_button_click(n_clicks, username, password):

    #### Creating a dict with all surgeon names and usernames
    
    
    
    #df = df[df['Primary Surgeon'] == USER_TO_NAME[username]]
    
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
    html.H1('Fixus', style={'font-family' : 'cursive','padding' : '0px 30px', 'font-size' : '60px', 'text-decoration': 'bold', 'font-style': 'oblique',
                       'font-variant': 'small-caps', 'font-stretch': 'ultra-expanded', 'text-align':'center'}),
    html.H1('MAIN MENU', style={'font-family' : 'Helvetica', 'font-size' : '20px', 'text-decoration': 'bold', 'padding': '0px 30px',
                                'backgroundColor': 'rgb(220, 248, 285)', 'text-align': 'center'}),
    html.Div([
        dcc.Link('MGB Dashboard', href='/page-1', style={'font-family' : 'Helvetica', 'font-size' : '15px', 'text-decoration': 'bold', 'text-align':'center', 'padding' : '30px 10px'}),
        html.Br(),
        html.Br(),
        dcc.Link('Models Page', href='/page-2', style={'font-family' : 'Helvetica', 'font-size' : '15px', 'text-decoration': 'bold', 'text-align':'center', 'padding' : '30px 10px'}),
        html.Br(),
        html.Br(),
        dcc.Link('Soomin Models Page', href='/page-3', style={'font-family' : 'Helvetica', 'font-size' : '15px', 'text-decoration': 'bold', 'text-align':'center', 'padding' : '30px 10px'}),
        html.Br()
        ], style ={'border-top': '1px gray solid', 'border-bottom': '1px gray solid', 'justify-content':'center', 'display': 'flex'}),
    html.Img(src = 'https://i1.wp.com/onlyvectorbackgrounds.com/wp-content/uploads/2019/03/Subtle-Lines-Abstract-Gradient-Background-Cool.jpg?fit=1191%2C843', width = '100%', height='400px')
], style={ 'width':'100%'})



### MGB Information Collection and Formatting ###

(AJRRPat_total, males_ratio, female_ratio, avg_length_of_stay, avg_BMI, avg_pat_age) = pat_glance_info(df)

##TODO: when adding another graph make sure to add it here
(proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar,discharge_distr_pie,  
 pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, pat_age_bar, bmi_bar) = create_current_graphs(df)

"""
(proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar, ICD10_bar, discharge_distr_pie, financial_pie, revenue_location_pie, 
 provider_specialty_bar, pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, pat_age_bar, bmi_bar, diag_gen_bar, alc_use_bar, alc_use_type_pie, tableBMI) = create_current_graphs(df, df_diag)

"""

# the whole blue row on the dashboard that gives patient info at a glance

pat_info_at_glance =  html.Div([

                            html.H4(children ='Patient Information At A Glance', style={'text-align': 'center'}),

                            html.Div([

                                dbc.Card([

                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Total patients'], className = 'card-title',

                                                        style ={'textAlign': 'center','color': '#0074D9'}),

                                                html.P(AJRRPat_total, className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                            ])

                                    ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                ], style={'display': 'inline-block', 'padding':'10px, 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Institution', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P('All MGB', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average patient age', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(avg_pat_age, className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Sex Ratio', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(str(males_ratio) + '% males and ' + str(female_ratio) + '% females', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average patient BMI', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(avg_BMI, className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average hospitalization duration', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(avg_length_of_stay, className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),
                            
                            
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

pat_age = html.Div([
                    html.Div([
                        dcc.Graph(figure = pat_age_bar)
                        ])
                    ])

pat_race_and_eth = html.Div([
                                html.Div([

                                    dcc.Graph(figure = pat_race_bar)

                                     ], style={'width': '50%','display': 'inline-block'}),              
                                html.Div([
                                        dcc.Graph(figure = pat_eth_bar)
                                        ], style={'width': '50%','display': 'inline-block'})
                            ], style={'width': '100%', 'display': 'inline-block'})
"""
pat_bmi = html.Div([
                html.Div([
                            dcc.Graph(figure = bmi_bar)
                        ], style={'width' : '50%', 'display': 'inline-block'}),
                html.Div([
                            dbc.Container([
                                    dbc.Label("Patient's BMI"),
                                    dbc.Table(tableBMI),
                                    dbc.Alert(id='tbl1')
                                ])
                        ], style={'width' : '50%', 'display': 'inline-block'})
                    ])
"""
pat_bmi = html.Div([
                html.Div([
                            dcc.Graph(figure = bmi_bar)
                        ], style={'width' : '50%', 'display': 'inline-block'})
                    ])

surg_info_header = html.Div([

                              html.Div([

                                      html.H2([

                                          "Surgeon Related Data"

                                              ])

                                      ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                              ], style={'backgroundColor': 'rgb(220, 248, 285)', 'display': 'inline-block','width':'100%'})
"""
pat_diag_gen = html.Div([
                    html.Div([
                                dcc.Graph(figure = diag_gen_bar)
                            ])
                    ])
"""

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

                          dcc.Graph(figure = proc_distr_pie)

                          ], style={'width': '50%','display': 'inline-block'}),
                 
                 html.Div([

                          dcc.Graph(figure = proc_revision_pie)

                          ], style={'width': '50%','display': 'inline-block'})

                ])

proc_hip_and_knee = html.Div([

                html.Div([

                        dcc.Graph(figure = hip_distr_bar)

                        ], style={'width': '50%', 'display': 'inline-block'}), 
                
                html.Div([

                        dcc.Graph(figure = knee_distr_bar)

                        ], style={'width': '50%', 'display': 'inline-block'})
                ])

substances_info  = html.Div([

                        html.Div([

                                html.H5([

                                        "Alcohol, Tobacco, and Drug Use History"

                                        ])

                                ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                        ], style={'backgroundColor': 'rgb(224, 224, 255)', 'display': 'inline-block', 'width': '100%'})


"""
alc_use = html.Div([
                html.Div([
                        dcc.Graph(figure = alc_use_bar)
                        ], style={'width': '100%','display': 'inline-block'})
                    ])

alc_use_type = html.Div([
                html.Div([
                        dcc.Graph(figure = alc_use_type_pie)
                        ], style = {'width': '50%', 'display': 'inline-block'})
                        ])
"""

## Comorbidities and complications category

comorb_info  = html.Div([

                        html.Div([

                                html.H5([

                                        "Comorbidities and complications"

                                        ])

                                ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                        ], style={'backgroundColor': 'rgb(224, 224, 255)', 'display': 'inline-block', 'width': '100%'})

"""
comorb_ICD10Top10 = html.Div([

                html.Div([

                        dcc.Graph(figure = ICD10_bar)
                       

                        ], style={'width': '100%','display': 'inline-block'})

                ])
"""

other_info  = html.Div([

                        html.Div([

                                html.H5([

                                        "Other patient related information"

                                        ])

                                ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                        ], style={'backgroundColor': 'rgb(224, 224, 255)', 'display': 'inline-block', 'width': '100%'})

prom_discharge = html.Div([

                            html.Div([

                                    dcc.Graph(figure = discharge_distr_pie)

                                    ])

                          ])

## Financial information category

inst_info_header = html.Div([

                              html.Div([

                                      html.H2([

                                          "Institution Related Data"

                                              ])

                                      ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                              ], style={'backgroundColor': 'rgb(220, 248, 285)', 'display': 'inline-block','width':'100%'})


fin_info = html.Div([

                        html.Div([

                                html.H5([

                                        "Financial Information"

                                        ])

                                ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                        ], style={'backgroundColor': 'rgb(224, 224, 255)', 'display': 'inline-block', 'width': '100%'})



"""
fin_patAndRev = html.Div([

                html.Div([

                        dcc.Graph(figure = financial_pie)

                        ], style={'width': '50%','display': 'inline-block'}),

                html.Div([

                        dcc.Graph(figure = revenue_location_pie)

                        ], style={'width': '50%','display': 'inline-block'})

                ])

fin_pat = html.Div([

                html.Div([

                        dcc.Graph(figure = financial_pie)

                        ], style={'width': '50%','display': 'inline-block'})

                ])
"""

##Institution information

inst_info = html.Div([

                        html.Div([

                                html.H5([

                                        "Institution Information"

                                        ])

                                ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                        ], style={'backgroundColor': 'rgb(224, 224, 255)', 'display': 'inline-block', 'width': '100%'})




"""

inst_prov = html.Div([

                            html.Div([

                                    dcc.Graph(figure = provider_specialty_bar)

                                    ], style={'width': '50%','display': 'inline-block'})

                            ])
"""
proc_diag = html.Div([
    
                html.Div([
                    
                        dcc.Graph(figure = hip_diag_bar)
                        
                        ], style={'width': '50%','display': 'inline-block'}),
                
                html.Div([
                    
                        dcc.Graph(figure = knee_diag_bar)
                        
                        ], style={'width': '50%','display': 'inline-block'})
                
                ])



### Surgeon related info tab ###

pat_tab_glance = html.Div([

                                html.H4(children ='Patient Information At A Glance', style={'text-align': 'center'}),

                                html.Div([

                                    dbc.Card([

                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Total patients'], className = 'card-title',

                                                        style ={'textAlign': 'center','color': '#0074D9'}),

                                                html.P(id='num_patients', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                    ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                        ], style={'display': 'inline-block', 'padding':'10px, 10px'}),

                                html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Institution', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P('-', className='card-content',

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

                                                            html.P(id='sex_ratio', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                        ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                                html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average patient BMI', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(id='avgBMI', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                        ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                                html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average hospitalization duration', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(id='avg_stay', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'350px', 'height':'100px', 'display': 'inline-block'})

                                        ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                                html.Div([

                                    html.H4('', className= 'card-title',

                                                style={'textAlign': 'center','color': '#0074D9'}),

                                    html.P('', className='card-content',

                                               style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                              ],  style={'backgroundColor': 'rgb(220, 248, 285)'})

                                ], style={'backgroundColor': 'rgb(220, 248, 285)'})



pat_bmi_tab = html.Div([
                html.Div([
                            dcc.Graph(id = 'bmi_bar')
                        ])
                    ])


pat_age_tab = html.Div([
                    html.Div([
                        dcc.Graph(id = 'pat_age_bar')
                        ])
                    ])

proc_total_tab = html.Div([

                 html.Div([

                          dcc.Graph(id = 'proc_distr_pie')

                          ], style={'width': '50%','display': 'inline-block'}),
                 
                 html.Div([

                          dcc.Graph(id = 'proc_revision_pie')

                          ], style={'width': '50%','display': 'inline-block'})

                ])

proc_hip_and_knee_tab = html.Div([

                html.Div([

                        dcc.Graph(id = 'hip_distr_bar')

                        ], style={'width': '50%', 'display': 'inline-block'}), 
                
                html.Div([

                        dcc.Graph(id = 'knee_distr_bar')

                        ], style={'width': '50%', 'display': 'inline-block'})
                ])

"""
comorb_ICD10Top10_tab = html.Div([

                html.Div([

                        dcc.Graph(id = 'ICD10_bar')
                       

                        ], style={'width': '100%','display': 'inline-block'})

                ])
"""

prom_discharge_tab = html.Div([

                            html.Div([

                                    dcc.Graph(id = 'discharge_distr_pie')

                                    ])

                          ])
"""
fin_patAndRev_tab = html.Div([

                html.Div([

                        dcc.Graph(id = 'financial_pie')

                        ], style={'width': '50%','display': 'inline-block'}),

                html.Div([

                        dcc.Graph(id = 'revenue_location_pie')

                        ], style={'width': '50%','display': 'inline-block'})
                ])

fin_pat_tab = html.Div([

                html.Div([

                        dcc.Graph(id = 'financial_pie')

                        ], style={'width': '50%','display': 'inline-block'})
                ])

"""
                                  
pat_race_and_eth_tab = html.Div([
                                html.Div([

                                    dcc.Graph(id = 'pat_race_bar')

                                     ], style={'width': '50%','display': 'inline-block'}),              
                                html.Div([
                                        dcc.Graph(id = 'pat_eth_bar')
                                        ], style={'width': '50%','display': 'inline-block'})
                            ], style={'width': '100%', 'display': 'inline-block'})

proc_diag_tab = html.Div([
    
                html.Div([
                    
                        dcc.Graph(id = 'hip_diag_bar')
                        
                        ], style={'width': '50%','display': 'inline-block'}),
                
                 html.Div([
                    
                        dcc.Graph(id = 'knee_diag_bar')
                        
                        ], style={'width': '50%','display': 'inline-block'})
                
                ])

#####THIS IS THE MAIN DASHBOARD PAGE LAYOUT: please don't clutter

page_1_layout = html.Div([

            dcc.Link('Go back to home', href='/'),
            html.Div([

                html.H3("Analytics Dashboard")], style={'textAlign': 'center'}),
          
            
            dcc.Tabs([
                    dcc.Tab(label = 'MGB Patients', children = [
                                                              pat_info_at_glance,
                                                                                                                            
                                                              html.Br(),
                                                              
                                                              pat_info_header,
                                                              
                                                              pat_age,
                                                              
                                                              pat_race_and_eth,
                                                              
                                                              pat_bmi,
                                                              
                                                              substances_info,
                                                              
                                                              #alc_use,
                                                              
                                                              #alc_use_type,
                                                              
                                                              comorb_info,

                                                              #comorb_ICD10Top10,
                                                              
                                                              other_info,
                                                              
                                                              prom_discharge,
                                                              
                                                              surg_info_header,

                                                              proc_info,

                                                              proc_total,

                                                              proc_hip_and_knee,
                                                              
                                                              proc_diag,
                                                              
                                                              #pat_diag_gen,

                                                              inst_info_header,
                                                              
                                                              #fin_patAndRev,
                                                              #fin_pat 
                                                            ]),

                        dcc.Tab(label= 'Your patients', children = [
                                                                pat_tab_glance,
                                                                                                                                
                                                                html.Br(),
                                                              
                                                                pat_info_header,
                                                                
                                                                pat_age_tab,
                                                                
                                                                pat_race_and_eth_tab,
                                                                
                                                                pat_bmi_tab,
                                                                
                                                                comorb_info,
                                                                
                                                                #comorb_ICD10Top10_tab,
                                                                
                                                                other_info,
                                                                
                                                                prom_discharge_tab,
                                                                
                                                                surg_info_header,

                                                                proc_total_tab,
                                                                
                                                                proc_hip_and_knee_tab,
                                                                
                                                                proc_diag_tab,
                                                                
                                                                inst_info_header,
                                                                
                                                                #fin_patAndRev_tab
                                                                #fin_pat_tab
                                                                
                                                                ])
                        ])
])





########### MODEL DEPLOYMENT LAYOUT DEFINITION
def model_image_view_html(id_upload, id_output_img, title_name="Default Model", select_button_name="Select Images"):
    layout = html.Div([
                    html.Div(className='container',
                      children=[
                                dbc.Row(html.H1(title_name), style={'textAlign': 'center'}),
                                dbc.Row(html.H1(" ")),
                                dbc.Row(
                                    html.Div([
                                            dcc.Upload(
                                                id=id_upload,
                                                children=html.Div([
                                                    'Drag and Drop or ',
                                                    html.A(select_button_name)
                                                ]),
                                                style={
                                                    'width': '100%',
                                                    'height': '60px',
                                                    'font-size': '22px',
                                                    'lineHeight': '60px',
                                                    'borderWidth': '1px',
                                                    'borderStyle': 'dashed',
                                                    'borderRadius': '5px',
                                                    },
                                                # Allow multiple files to be uploaded
                                                multiple=True),
                                            html.Div(id=id_output_img, style={'textAlign': 'center'})
                                            ])
                                            
                                        , style={'textAlign': 'center'}),
                                ]
                        ),
                    html.Br(),
                    dcc.Link('Go to Page 1', href='/page-1'),
                    html.Br(),
                    dcc.Link('Go back to home', href='/')
                    ])
                    
    return layout
    


########################## START: PAGE 2

page_2_layout = model_image_view_html(id_upload= 'upload-image', id_output_img= 'output-image-upload',
                                      title_name= "Hip Fracture Detection Models", select_button_name = "Select Hip Radiographs")

@app.callback(Output('output-image-upload', 'children'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents_hip_fracture(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]

        return children    
    
### IMAGE LOADERS
def parse_contents_hip_fracture(contents, filename, date):

    ### READ IMAGE AND RESIZE
    im_bytes = base64.b64decode(contents.split("base64,")[-1])
    im_arr   = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

    # Preprocessing
    img_new = im_preprocess(img, im_newsize = (1062, 1062))
    
    # Encoding Back
    _, im_arr   =  cv2.imencode('.png', img_new)  # im_arr: image in Numpy one-dim array format.
    encoding =  base64.b64encode(im_arr)
    image    = 'data:image/png;base64,{}'.format(encoding.decode())

    # Get the Prediction
    prediction  = read_image_and_classify(img_new)


    output_view = html.Div([
                            html.H5(filename),
                            html.H6(datetime.datetime.fromtimestamp(date)),

                            # HTML images accept base64 encoded strings in the same format
                            # that is supplied by the upload
                            html.Div('Pre-processed Image'),        
                            html.Img(src=image, style={'height': '256px'}),
                            # html.Div('Actual Image'),
                            # html.Img(src=contents, style={'height': '500px'}),
                            html.Hr(),
                            html.Div('Prediction: {}'.format(prediction)),
                            html.Pre(contents[0:200] + '...', style={
                                'whiteSpace': 'pre-wrap',
                                'wordBreak': 'break-all'
                            })
                        ], style={'textAlign': 'center'})

    return output_view


### ML Preprocessor
def read_image_and_classify(image_in):

    image_width  = 1062 #384
    image_height = 1062 #384
    max_im_size = image_width
    n_channel = 3
    class_names = ['Control','Fracture']

    # # 3) Making the predictions
    student_images = np.zeros((1, image_width, image_height, n_channel))

    ## Preprocessing
    for channel in range(n_channel):
        student_images[0, :, :, channel] = image_in


    # Use the Model to Predict the Image
    student_images = student_images.astype(np.uint8)

    prediction_prob = [0.66, 0.34]
    predicted_class = prediction_prob[0]
    # predicted_class = tf.argmax(input=prediction_prob, axis=1).numpy()
    
    return predicted_class



########################## END: PAGE 2



########################## START: PAGE 3

page_3_layout = model_image_view_html(id_upload= 'upload-image-soomin', id_output_img= 'output-image-upload-soomin',
                                      title_name= "Hello Soomin!", select_button_name = "Select Radiographs")

@app.callback(Output('output-image-upload-soomin', 'children'),
              Input('upload-image-soomin', 'contents'),
              State('upload-image-soomin', 'filename'),
              State('upload-image-soomin', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents_hip_fracture(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]

        return children    
    
### IMAGE LOADERS
def parse_contents_soomin(contents, filename, date):

    ### READ IMAGE AND RESIZE
    im_bytes = base64.b64decode(contents.split("base64,")[-1])
    im_arr   = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

    # Preprocessing
    # TODO: Soomin adds her preprocessing stuff here
    img_new = img_new
    
    # Encoding Back
    _, im_arr   =  cv2.imencode('.png', img_new)  # im_arr: image in Numpy one-dim array format.
    encoding =  base64.b64encode(im_arr)
    image    = 'data:image/png;base64,{}'.format(encoding.decode())

    # Get the Prediction
    # TODO: Soomin adds her preprocessing stuff here
    prediction  = 0.5000000

    output_view = html.Div([
                            html.H5(filename),
                            html.H6(datetime.datetime.fromtimestamp(date)),

                            # HTML images accept base64 encoded strings in the same format
                            # that is supplied by the upload
                            html.Div('Pre-processed Image'),        
                            html.Img(src=image, style={'height': '256px'}),
                            # html.Div('Actual Image'),
                            # html.Img(src=contents, style={'height': '500px'}),
                            html.Hr(),
                            html.Div('Prediction: {}'.format(prediction)),
                            html.Pre(contents[0:200] + '...', style={
                                'whiteSpace': 'pre-wrap',
                                'wordBreak': 'break-all'
                            })
                        ], style={'textAlign': 'center'})

    return output_view


### ML Preprocessor
def read_image_and_classify_soomin(image_in):

    pass



########################## END: PAGE 2





############################## USER STATUS
@app.callback(Output('user-status-div', 'children'), Output('login-status', 'data'), [Input('url', 'pathname')])
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
    

#Surgeon specific patient info at a glance
@app.callback(
    Output('num_patients','children'), 
    Output('sex_ratio','children'),
    Output('avg_stay', 'children'),
    Output('avgBMI', 'children'),
    Output('avgAge', 'children'),
    [Input('login-status','data')])
def update_pat_info(username):
    global USER_TO_NAME
    if username in USER_TO_NAME.keys():
        try: 
            #USER_TO_NAME mapped to surgeon first and last name
            sur_first_last = USER_TO_NAME[username].rsplit(' ',1)
            cond1 = df.SurFirstName == sur_first_last[0]
            cond2 = df.SurLastName == sur_first_last[1]
            df_surgeon = df.loc[cond1 & cond2]
            
            (AJRRPat_total, males_ratio, female_ratio, avg_length_of_stay, avg_BMI, avg_pat_age) = pat_glance_info(df_surgeon)

            AJRRPat_total_output = '{}'.format(AJRRPat_total)
            sex_ratio_output = '{}% males and {}% females'.format(males_ratio, female_ratio)           
            avg_stay_output = '{}'.format(avg_length_of_stay)
            avg_BMI_output = '{}'.format(avg_BMI)
            avg_age_output = '{}'.format(avg_pat_age)
            
            return (AJRRPat_total_output, sex_ratio_output, avg_stay_output, avg_BMI_output, avg_age_output)
        except:  
            return ('', '','', '', '')
    else:
        return ('','','', '', '')


#Surgeon specific graphs
@app.callback(
    Output('proc_distr_pie','figure'),
    Output('proc_revision_pie','figure'),
    Output('hip_distr_bar', 'figure'),
    Output('knee_distr_bar','figure'),
    #Output('ICD10_bar','figure'),
    Output('discharge_distr_pie','figure'),
    #Output('financial_pie','figure'),
    #Output('revenue_location_pie','figure'),
    Output('pat_race_bar', 'figure'),
    Output('pat_eth_bar', 'figure'),
    Output('hip_diag_bar','figure'),
    Output('knee_diag_bar','figure'),
    Output('pat_age_bar', 'figure'),
    Output('bmi_bar', 'figure'),
    [Input('login-status','data')])
def update_sur_spec_info(username):

    if username in USER_TO_NAME.keys():
        """
        try: 
            
            df_surgeon = df[df['surgeons.PrimarySurgeon'] == USER_TO_NAME[username]]

            (proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar, ICD10_bar, discharge_distr_pie, financial_pie, 
             revenue_location_pie, provider_specialty_bar, pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, 
             pat_age_bar, bmi_bar) = create_current_graphs(df_surgeon, df, df_diag)

            
            return (proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar, ICD10_bar, discharge_distr_pie, financial_pie, #revenue_location_pie, 
                    pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, pat_age_bar, bmi_bar, alc_use_bar, alc_use_type)
        except:  
            return ('','','','','','','','','','','','','', '', '')
    else:
        return ('','','','','','','','','','','','', '', '', '', '')
    """
        try:
            
            #USER_TO_NAME mapped to surgeon first and last name
            sur_first_last = USER_TO_NAME[username].rsplit(' ',1)
            cond1 = df.SurFirstName == sur_first_last[0]
            cond2 = df.SurLastName == sur_first_last[1]
            df_surgeon = df.loc[cond1 & cond2]
            
            (proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar, discharge_distr_pie, 
             pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, pat_age_bar, bmi_bar) = create_current_graphs (df_surgeon)
        
            return (proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar, discharge_distr_pie, 
                    pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, pat_age_bar, bmi_bar )
        
        except:
            return ('','','','','','','','','','','')
    else:
        return ('','','','','','','','','','','')
        
    


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
    elif pathname == '/page-2':
        if current_user.is_authenticated:
            view = page_2_layout
        else:
            view = 'Redirecting to login...'
            url = '/login'
    elif pathname == '/page-3':
        if current_user.is_authenticated:
            view = page_3_layout
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
    page_2_layout,
    page_3_layout
])



if __name__ == '__main__':
    app.run_server(debug=True)