# Read Required Libraries
import os
import sys

from flask import Flask
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

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
from datetime import date

from codes.create_graphs import create_current_graphs, nongraph


#### FIXUS BEGINS
PATHS = {
    'images': os.path.join('images'),
    'app_data' : os.path.join('data','app_data'),
    'data_aaos' : os.path.join('data','aaos_database')
    }

### Loading Data for MGB Dashboard
file_name = os.path.join(PATHS['app_data'], 'app_data_final.pkl')
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
                title='Fixus App v0.1.0',
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
                  html.Button(children='LOGIN', n_clicks=0, style={'backgroundColor': 'crimson', 'border-color': '#F5FFFA', 'color' : '#F5FFFA', 'font-size': '20px', 'padding': '10px 25px'},
                              type='submit', id='login-button'),
                  html.Div(children='', id='output-state'),
                  html.Br(),
                  dcc.Link('Home', href='/')], 
                  style={'backgroundColor': 'rgb(248,244,244)', 'display': 'inline-block','width':'100%', 'text-align': 'center'})
# Successful login screen
success = html.Div([html.Div([html.H2('Login successful.'),
                              html.Br(),
                              dcc.Link('Home', href='/')], style={'backgroundColor': 'rgb(248,244,244)', 'display': 'inline-block','width':'100%'})  # end div
                    ], 
                   style={'backgroundColor': 'rgb(248,244,244)', 'display': 'inline-block','width':'100%', 'text-align': 'center'})  # end div
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
                   ], style={'backgroundColor': 'rgb(248,244,244)', 'display': 'inline-block','width':'100%'})  # end div



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
    html.Hr(style={'borderColor':'crimson'}),
    html.Br(),
    html.Div(id='page-content'),
])

app.layout = post_login_content


#####src= os.path.join(PATHS['images'], 'sorglogo.png')
index_page = html.Div([
    html.H1('FIXUS', style={'font-family' : 'Geneva','padding' : '0px 30px', 'font-size' : '60px', 'text-decoration': 'bold',
                       'font-stretch': 'ultra-expanded', 'text-align':'center', 'color': 'crimson'}),
    html.H1('Welcome to the MAIN MENU!', style={'font-family' : 'Helvetica', 'font-size' : '30px', 'text-decoration': 'bold', 'padding': '0px 30px',
                                'backgroundColor': 'rgb(248,244,244)', 'text-align': 'center'}),
    html.Div([
        dcc.Link('MGB Dashboard', href='/page-1', style={'font-family' : 'Helvetica', 'font-size' : '25px', 'text-decoration': 'bold', 'text-align':'center', 'padding' : '30px 10px'}),
        html.Br(), 
    
        ], style ={'border-top': '1px gray solid', 'border-bottom': '0px gray solid', 'justify-content':'center', 'display': 'flex'}),
    html.Br(),
    html.H2('Our Vision', style={'font-family' : 'Helvetica', 'font-size' : '30px', 'text-decoration': 'bold', 'padding': '0px 30px',
                                 'text-align': 'center'}
            ),
    html.Br(),
    html.H3('To provide accessible and user friendly information. Striving to help our users interpret data to address problems. Providing the power of data analysis and visualization with one click.',
            style={'font-family' : 'Helvetica', 'font-size' : '20px', 'text-decoration': 'bold', 'padding': '0px 30px',  'text-align': 'center',
                                 'width':'100%', 'text-align': 'center'}
            ),
    html.Br(),
    
    html.Img(src = 'https://static.vecteezy.com/system/resources/previews/000/543/821/original/white-abstract-background-vector-gray-abstract-modern-design-background-for-report-and-project-presentation-template-vector-illustration-graphic-futuristic-and-circular-curve-shape.jpg',
             width = '100%', height='600px')
], style={ 'width':'100%','backgroundColor': 'rgb(248,244,244)' })


# the whole blue row on the dashboard that gives patient info at a glance
#THIS IS REALLY THE CONTAINER
row1 = html.Div([
    #ROW
        html.Div([
                #COLUMN
                            html.Div([
                                   
                                dbc.Card(
                                     html.Div([
                                         html.Div([
                                       dbc.Row([
                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Total procedures'], className = 'card-title',

                                                        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                html.P(id = 'total_proc', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '50px', 'color': 'black', 'text-decoration': 'bold'})

                                                    ])
                                                ]) ], style={'width':'400px', 'height':'250px', 'background-color': 'white'}), 
                                        html.Div([
                                        dbc.Row([
                                                dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Average length of stay'], className = 'card-title',

                                                        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                html.P(id = 'avg_length_of_stay', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '50px', 'color': 'black', 'text-decoration': 'bold'}), 
                                                
                                                html.P(id = 'stdev_len_of_stay', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '25px', 'color': 'gray', 'text-decoration': 'normal'})

                                                    ])
                                                ]) ],  style={'width':'400px', 'height':'280px', 'background-color': 'white'})
                                        ], style={'width':'400px', 'height':'200px', 'background-color': 'white'})
                                        )
                                    ], style={'display': 'inline-block', 'padding': '5px', 'padding-left': '100px'}
                                    ), 
                    #COLUMN
                            html.Div([
                                html.Div([
                                 dbc.Card(
                                        [
                                        dbc.CardBody([
                                                        html.H4('Sex Distribution', className = 'card-title',
                                                                style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'})
                                                    ]),
                                         dcc.Graph(id = 'gender_graph')
                                                 ], body=True, style={'width':'400px', 'height':'565px', 'backgroundColor': 'white'}
                                         )
                                        ])
                                    ], style={'display': 'inline-block', 'padding': '5px'}
                                    ),
                    #COLUMN
                            html.Div([
                                html.Div([
                                 dbc.Card(
                                        [
                                        dbc.CardBody([
                                                        html.H4('Age Distribution', className = 'card-title',
                                                                style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}), 
                                                        
                                                        html.P(id = 'mean_age', className = 'card-content',
                                                                style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '25px', 'color': 'gray', 'text-decoration': 'normal'} 
                                                                )
                                                    ]),
                                         dcc.Graph(id = 'pat_age_bar')
                                                 ], body=True, style={'width':'600px', 'height':'565', 'backgroundColor': 'white'},
                                         )
                                        ])
                                    ], style={'display': 'inline-block', 'padding': '5px'}
                                    ), 
                    #COLUMN
                            html.Div([
                                html.Div([
                                 dbc.Card(
                                        [
                                        dbc.CardBody([
                                                        html.H4('Patient Location Distribution', className = 'card-title',
                                                                style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'})
                                                    ]),
                                         html.Img(src ='https://media.istockphoto.com/vectors/map-of-massachusetts-vector-id1048768466?k=6&m=1048768466&s=170667a&w=0&h=732KyrYHStgD9fq1G6PbKzd1m9LzMpK1AlffIdavnkA=')
                                                 ], body=True, style={'width':'800px', 'height':'565px', 'backgroundColor': 'white'}
                                         )
                                        ])
                                    ], style={'display': 'inline-block', 'padding': '5px', 'padding-right': '100px'}
                                    )
                ], style={'display' : 'flex'}), 
        html.Br()
        ], style={'textAlign' : 'center'})

#row2
row2 = html.Div([
    #ROW
        html.Div([
                #COLUMN
                            html.Div([
                                   
                                dbc.Card([
                                     html.Div([
                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Top 10 Diagnoses - based on ICD10-DX'], className = 'card-title',

                                                        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                    ]), 
                                        dcc.Graph(id = 'diag_bar')
                                        ], style={'width':'600px', 'height':'400px', 'background-color': 'white'})
                                        ], body=True, style={'width':'600px', 'height':'550px', 'backgroundColor': 'white'})
                                    ], style={'display': 'inline-block', 'padding': '5px', 'padding-left': '100px'}
                                    ), 
                    #COLUMN
                            html.Div([
                                   
                                dbc.Card([
                                     html.Div([
                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Procedures - based on CPTs'], className = 'card-title',

                                                        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                    ]), 
                                        dcc.Graph(id = 'proc_bar')
                                        ], style={'width':'850px', 'height':'400px', 'background-color': 'white'})
                                        ], body=True, style={'width':'850px', 'height':'550px', 'backgroundColor': 'white'})
                                    ], style={'display': 'inline-block', 'padding': '5px'}
                                    ), 
                    #COLUMN
                            html.Div([
                                html.Div([
                                 dbc.Card(
                                        [
                                        dbc.CardBody([
                                                        html.H4('Charlson Comorbidity Index', className = 'card-title',
                                                                style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'})
                                                    ]),
                                         dcc.Graph(id = 'CCI_bw')
                                                 ], body=True, style={'width':'765px', 'height':'550px', 'backgroundColor': 'white'}
                                         )
                                        ])
                                    ], style={'display': 'inline-block', 'padding': '5px'}
                                    ), 
                   
                ], style={'display' : 'flex'}), 
        html.Br()
        ], style={'textAlign' : 'center'})

#row4
row4 = html.Div([
    #ROW
        html.Div([
                #COLUMN
                            html.Div([
                                   
                                dbc.Card([
                                     html.Div([
                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Revision'], className = 'card-title',

                                                        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                    ]), 
                                        dcc.Graph(id = 'proc_revision_pie')
                                        ], style={'width':'600px', 'height':'400px', 'background-color': 'white'})
                                        ], body=True, style={'width':'600px', 'height':'550px', 'backgroundColor': 'white'})
                                    ], style={'display': 'inline-block', 'padding': '5px', 'padding-left': '100px'}
                                    ), 
                    #COLUMN
                            html.Div([
                                   
                                dbc.Card([
                                     html.Div([
                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['90-Days Patient Readmission Rate'], className = 'card-title',
                                                        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),
                                                 html.P(id = 'day90read', className = 'card-content',
                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '40px', 'color': 'black', 'text-decoration': 'bold', 'padding' : '100px'}),
                                                 html.P(id = 'day90readtotal', className = 'card-content',
                                                        style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '25px', 'color': 'gray', 'text-decoration': 'normal', 'padding' : '50px'})

                                                    ])
                                        ], style={'width':'850px', 'height':'400px', 'background-color': 'white'})
                                        ], body=True, style={'width':'850px', 'height':'550px', 'backgroundColor': 'white'})
                                    ], style={'display': 'inline-block', 'padding': '5px'}
                                    ), 
                    #COLUMN
                            html.Div([
                                html.Div([
                                 dbc.Card(
                                        [
                                        dbc.CardBody([
                                                        html.H4('Discharge Distribution', className = 'card-title',
                                                                style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'})
                                                    ]),
                                         dcc.Graph(id = 'discharge_distr_pie')
                                                 ], body=True, style={'width':'765px', 'height':'550px', 'backgroundColor': 'white'}
                                         )
                                        ])
                                    ], style={'display': 'inline-block', 'padding': '5px'}
                                    ), 
                   
                ], style={'display' : 'flex'}), 
        html.Br()
        ], style={'textAlign' : 'center'})

#row3
row3 = html.Div([
    #ROW
        html.Div([
                #COLUMN
                            html.Div([
                                   
                                dbc.Card([
                                     html.Div([
                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Tobacco Use'], className = 'card-title',

                                                        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                    ]), 
                                        dcc.Graph(id = 'tob_use_bar')
                                        ], style={'width':'900px', 'height':'400px', 'background-color': 'white'})
                                        ], body=True, style={'width':'900px', 'height':'550px', 'backgroundColor': 'white'})
                                    ], style={'display': 'inline-block', 'padding': '5px', 'padding-left': '100px'}
                                    ), 
                    #COLUMN
                            html.Div([
                                   
                                dbc.Card([
                                     html.Div([
                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Percentage of Patients Filling Out PROMs'], className = 'card-title',

                                                        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                html.P(id = 'preop_proms', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '30px', 'color': 'black', 'text-decoration': 'bold', 'padding':'10px'}),
                                                
                                                html.P('patients who filled out at least one pre-op questionnaire', className = 'card-content',

                                                      style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '20px', 'color': 'gray', 'text-decoration': 'normal', 'padding' : '10px'}),
                                                
                                                html.P(id = 'postop_proms', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '30px', 'color': 'black', 'text-decoration': 'bold'}),
                                                
                                                html.P('patients who filled out at least one post-op questionnaire', className = 'card-content',

                                                      style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '20px', 'color': 'gray', 'text-decoration': 'normal', 'padding' : '10px'}),
                                                
                                                html.P(id = 'bothproms_final', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '30px', 'color': 'black', 'text-decoration': 'bold'}),
                                                
                                                html.P('patients who filled out at least one pre-op and one post-op PROMs questionnaire', className = 'card-content',

                                                      style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '20px', 'color': 'gray', 'text-decoration': 'normal', 'padding' : '5px'}),
                                                
                                                html.P(id = 'numbothproms', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '30px', 'color': 'white', 'text-decoration': 'bold'})
                                                
                                                

                                                    ]), 
                            
                                        ])
                                        ], body=True, style={'width':'700px', 'height':'550px', 'backgroundColor': 'white'})
                                    ], style={'display': 'inline-block', 'padding': '5px'}
                                    ), 
                    #COLUMN
                           html.Div([
                                  
                               dbc.Card([
                                    html.Div([
                                       dbc.CardBody([

                                               html.H4(id='card-title-1', children= ['PROMs Filled Out per Patient'], className = 'card-title',

                                                       style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                html.P(id = 'preop_proms_perpt', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '40px', 'color': 'black', 'text-decoration': 'bold', 'padding':'20px'}),
                                                
                                                 html.P('pre-op questionnaires', className = 'card-content',

                                                      style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '20px', 'color': 'gray', 'text-decoration': 'normal', 'padding' : '5px'}),
                                                
                                                html.P(id = 'postop_proms_perpt', className = 'card-content',

                                                       style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '40px', 'color': 'black', 'text-decoration': 'bold'}),
                                                
                                                 html.P('post-op questionnaires', className = 'card-content',

                                                      style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '20px', 'color': 'gray', 'text-decoration': 'normal', 'padding' : '5px'}),
                                                 
                                                 html.P('*The questionnaires included in our measurements are PROMIS-10, PROMIS physical function, PROMS KOOS, PROMS HOOS, MSK CUSTOM, JOINT FUNCTION & PAIN, PROMIS PAIN INTERFERENCE, MSK BCTI,PROMS RISK ASSESSMENT AND PREDICTION TOOL, MSK QUICK DASH, ANXIETY, DEPRESSION, PROMS MSK LOW BACK PAIN,SUBSTANCE USE DISORDER QUESTIONNAIRE, FALLS SCREENING, PROMIS UPPER EXTREMITY FUNCTION, PROMS MOOR POST-OP CARE GOAL ACHIEVEMENT, PROMS MOOR PRE-OP EXPECTATION CARE GOAL ACHIEVEMENT, PROMS MOOR PRE-OP IMPORTANCE CARE GOAL ACHIEVEMENT', className = 'card-content',

                                                      style = {'textAlign':'center', 'font-family':'sans-serif', 'font-size': '10px', 'color': 'gray', 'text-decoration': 'normal', 'padding' : '5px'})

                                                   ]), 
                                       ])
                                       ], body=True, style={'width':'700px', 'height':'550px', 'backgroundColor': 'white'})
                                   ], style={'display': 'inline-block', 'padding': '5px'}
                                   ), 
                   
                ], style={'display' : 'flex'}), 
        html.Br()
        ], style={'textAlign' : 'center'})

# surg_info_header = html.Div([

#                               html.Div([

#                                       html.H2([

#                                           "Surgeon Related Data"

#                                               ])

#                                       ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center', 'font-family':'sans-serif'})

#                               ], style={'backgroundColor': 'rgb(248,244,244)', 'display': 'inline-block','width':'100%'})

#row5
row5 = html.Div([
    #ROW
        html.Div([
                #COLUMN
                            html.Div([
                                   
                                dbc.Card([
                                     html.Div([
                                        dbc.CardBody([

                                                html.H4(id='card-title-1', children= ['Top 10 Comorbidities - based on ICD10 DX'], className = 'card-title',

                                                        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                    ]), 
                                        dcc.Graph(id = 'comorb_bar')
                                        ], style={'width':'900px', 'height':'400px', 'background-color': 'white'})
                                        ], body=True, style={'width':'900px', 'height':'550px', 'backgroundColor': 'white'})
                                    ], style={'display': 'inline-block', 'padding': '5px', 'padding-left': '100px'}
                                    ), 
                    #COLUMN
                            html.Div([
                                   
                                dbc.Card([
                                     html.Div([
                                        dbc.CardBody([

                                               # html.H4(id='card-title-1', children= ['Percentage of Patients Filling Out PROMs'], className = 'card-title',

                                                #        style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                               

                                                    ]), 
                            
                                        ])
                                        ], body=True, style={'width':'700px', 'height':'550px', 'backgroundColor': 'white'})
                                    ], style={'display': 'inline-block', 'padding': '5px'}
                                    ), 
                    #COLUMN
                           html.Div([
                                  
                               dbc.Card([
                                    html.Div([
                                       dbc.CardBody([

                                              # html.H4(id='card-title-1', children= ['PROMs Filled Out per Patient'], className = 'card-title',
#
                                                       #style ={'padding-top': '10px', 'textAlign': 'center','color': '#c6c3c3', 'font-family':'sans-serif', 'font-size' : '25px'}),

                                                 ]), 
                                       ])
                                       ], body=True, style={'width':'700px', 'height':'550px', 'backgroundColor': 'white'})
                                   ], style={'display': 'inline-block', 'padding': '5px'}
                                   ), 
                   
                ], style={'display' : 'flex'}), 
        html.Br()
        ], style={'textAlign' : 'center'})


## Procedures and conditions

# proc_info = html.Div([

#                         html.Div([

#                                 html.H5([

#                                         "Procedures and condition related information"

#                                         ])

#                                 ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center', 'font-family':'sans-serif'})

#                         ], style={'backgroundColor': 'white', 'display': 'inline-block', 'width': '100%'})


# proc_total = html.Div([

#                  html.Div([

#                           dcc.Graph(id = 'proc_distr_pie')

#                           ], style={'width': '100%','display': 'inline-block'})

#                 ])


### DROPDOWNS

provider_dropdown = dcc.Dropdown(
    options=[{'label': 'All MGB Data', 'value': 'All'},
             {'label': 'My Data', 'value': 'Surgeon'}], 
    value='All', id='provider_dd', clearable = False)

div_dropdown = dcc.Dropdown(
    options=[{'label': 'Arthroplasty', 'value': 'AJRR'}],
    value='AJRR', id='div_dd', multi=False, clearable = False)

inst_dropdown = dcc.Dropdown(id='inst_dd', multi=False, clearable = False)

diag_dropdown = dcc.Dropdown(id='diag_dd', multi=True, clearable = False)

site_dropdown = dcc.Dropdown(id='site_dd', multi=False, clearable = False)

type_dropdown = dcc.Dropdown(id='type_dd', multi=True, clearable = False)

enc_daterange = dcc.DatePickerRange(id='enc_daterange', 
                                    min_date_allowed = date(2015,1,1),
                                    max_date_allowed = date(2021,12,31),
                                    initial_visible_month = date(2021,1,1),
                                    start_date = date(2021,1,1),
                                    end_date = date(2021,12,31))



filter_dropdowns = html.Div([
    html.Div([provider_dropdown], style={'width':'200px','height':'20px','display':'inline-block', 'font-family':'sans-serif', 'padding-left':'20px','padding-right':'20px'}),
    html.Div([div_dropdown], style={'width':'200px','height':'20px','display':'inline-block', 'font-family':'sans-serif', 'padding-right':'20px'}),
    html.Div([inst_dropdown], style={'width':'200px','height':'20px','display':'inline-block', 'font-family':'sans-serif', 'padding-right':'20px'}),
    html.Div([diag_dropdown], style={'width':'350px','height':'20px','display':'inline-block', 'font-family':'sans-serif','padding-right':'20px'}),
    html.Div([site_dropdown], style={'width':'350px','height':'20px','display':'inline-block', 'font-family':'sans-serif','padding-right':'20px'}),
    html.Div([type_dropdown], style={'width':'350px','height':'20px','display':'inline-block', 'font-family':'sans-serif','padding-right':'20px'}),
    html.Div([enc_daterange], style={'display':'inline-block','font-family':'sans-serif'})
    ], style={'text-align': 'center'})


#####THIS IS THE MAIN DASHBOARD PAGE LAYOUT

page_1_layout = html.Div([

            dcc.Link('Go back to home', href='/'),
            
            html.Div([

                html.H3('FIXUS Dashboard', style={'font-family' : 'GENEVA','padding' : '0px 10px', 'font-size' : '40px', 'text-decoration': 'bold', 
                                                  'font-variant': 'small-caps', 'font-stretch': 'ultra-expanded', 'text-align':'center', 'color': 'crimson'}),
            
                dcc.Tab(label = 'MGB Patients', children = [
                                                          filter_dropdowns,
                                                          
                                                          html.Br(),
                    
                                                          row1,
                                                          
                                                          row2,
                                                          
                                                          row3,
                                                                                                        
                                                          row4, 
                                                          
                                                          row5
                                                                                                                      
                                                          #surg_info_header,
    
                                                          #proc_info,
    
                                                          #proc_total
                                                          
                                                        ])
                       
                ])
            ], style={'background-color': 'rgb(248,244,244)'})





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
    Output('diag_dd','options'),
    Output('site_dd','options'),
    Output('type_dd','options'),
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
    inst_dd_options = [{'label':'All Institutions', 'value': 'All'}] + [{'label': i, 'value': i} for i in data.Hosp_name.unique()] 
    
    #setting diagnosis dropdown options
    main_diag = data.DX_Main_Category.unique()
    diag_dd_options = [{'label':'Primary Diagnoses', 'value': 'All'}] + [{'label': i, 'value': i} for i in main_diag]
    
    #setting procedure site dropdown options
    site_dd_options =  [{'label':'All Sites', 'value': 'All'}] + [{'label': i, 'value': i} for i in data.Procedure_site.unique()]
    
    #setting procedure type dropdown options
    type_dd_options =  [{'label':'All Procedures', 'value': 'All'}] + [{'label': i, 'value': i} for i in data.Main_CPT_category.unique()]
    
    return (inst_dd_options, diag_dd_options, site_dd_options, type_dd_options)

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

#Set procedure site dropdown value based on options
@app.callback(
    Output('site_dd', 'value'),
    Input('site_dd', 'options')
    )
def set_site_dd_value(available_options):
    return available_options[0]['value']

#Set procedure type dropdown value based on options
@app.callback(
    Output('type_dd', 'value'),
    Input('type_dd', 'options')
    )
def set_type_dd_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('total_proc','children'), 
    Output('avg_length_of_stay','children'),
    Output('stdev_len_of_stay', 'children'),
    Output('mean_age', 'children'),
    Output('preop_proms','children'),
    Output('postop_proms','children'),
    Output('preop_proms_perpt','children'),
    Output('postop_proms_perpt','children'),
    Output('day90read', 'children'),
    Output('day90readtotal', 'children'),
    Output('bothproms_final', 'children'),
    Output('numbothproms', 'children'),
    Input('login-status','data'),
    Input('provider_dd','value'),
    Input('inst_dd','value'),
    Input('diag_dd','value'),
    Input('site_dd','value'),
    Input('type_dd','value'),
    Input('enc_daterange','start_date'),
    Input('enc_daterange','end_date'))
def update_pat_info(username, provider, inst, diag, site, proc, start_date, end_date):
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
            

            
            if 'All' in inst:
                data = data
            else:
                data = data[data.Hosp_name == inst]
             
            #TODO: this errors just once when trying to delete the all diagnoses option --> why?
            if 'All' in diag:
                data = data
            else:
                data = data[data.DX_Main_Category.isin(diag)]
                
            if 'All' in site:
                data = data
            else:
                data = data[data.Procedure_site == site]
                
            if 'All' in proc:
                data = data
            else:
                data = data[data.Main_CPT_category.isin(proc)]   
                
            #Filter by date range
            data.Surg_date = pd.to_datetime(data.Surg_date)
            data = data[(data.Surg_date > start_date) & (data.Surg_date < end_date)]
            
            
            (total_proc, avg_length_of_stay, stdev_len_of_stay, BMI_total, avg_pat_age, stdev_age, preop_proms_pts, postop_proms_pts, preop_proms_perpt,
             postop_proms_perpt, day90read, day90readtotal, bothproms_final, numbothproms) = nongraph(data)

            mean_age_output = 'Mean age {} ± {}'.format(avg_pat_age, stdev_age)
            stdev_len_of_stay_output = '± {} hours'.format(stdev_len_of_stay)
            
            preop_proms_output = '{}%'.format(preop_proms_pts)
            postop_proms_output = '{}%'.format(postop_proms_pts)
            
            preop_proms_perpt_output = '{}'.format(preop_proms_perpt)
            postop_proms_perpt_output = '{}'.format(postop_proms_perpt)
            bothproms_final_output = '{}% ({} patients)'.format(bothproms_final, numbothproms)
            
            day90read_output = '{} readmitted patients'.format(day90read)
            day90readtotal_output = 'out of {} reported'.format(day90readtotal)
            
            return (total_proc, avg_length_of_stay, stdev_len_of_stay_output, mean_age_output, preop_proms_output, postop_proms_output, preop_proms_perpt_output,
                    postop_proms_perpt_output, day90read_output, day90readtotal_output, bothproms_final_output, numbothproms)
        except:  
            return ('', '','', '', '', '', '', '', '', '', '', '')
    else:
        return ('','','', '', '', '', '', '', '', '', '', '')


#Charts and graphs
@app.callback(
    Output('gender_graph','figure'),
    Output('pat_age_bar','figure'),
    Output('diag_bar','figure'),
    Output('proc_bar','figure'),
    Output('CCI_bw','figure'),
    Output('proc_revision_pie','figure'),
    #Output('alc_use_bar','figure'),
    #Output('alc_use_type_pie','figure'),
    Output('tob_use_bar','figure'),
    Output('discharge_distr_pie', 'figure'),
    Output('comorb_bar', 'figure'),
    Input('login-status','data'),
    Input('provider_dd','value'),
    Input('inst_dd','value'),
    Input('diag_dd','value'),
    Input('site_dd','value'),
    Input('type_dd','value'),
    Input('enc_daterange','start_date'),
    Input('enc_daterange','end_date'))
def update_graphs(username, provider, inst, diag, site, proc, start_date, end_date):
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
            
            if 'All' in inst:
                data = data
            else:
                data = data[data.Hosp_name == inst]
             
            #TODO: this errors just once when trying to delete the all diagnoses option --> why?
            if 'All' in diag:
                data = data
            else:
                data = data[data.DX_Main_Category.isin(diag)]
                
            if 'All' in site:
                data = data
            else:
                data = data[data.Procedure_site == site]
                
            if 'All' in proc:
                data = data
            else:
                data = data[data.Main_CPT_category.isin(proc)]   
                
            #Filter by date range
            data.Surg_date = pd.to_datetime(data.Surg_date)
            data = data[(data.Surg_date > start_date) & (data.Surg_date < end_date)]
            
            #CREATE GRAPHS
            (gender_graph, pat_age_bar, diag_bar, proc_bar, CCI_bw, proc_revision_pie, tob_use_bar, discharge_distr_pie, comorb_bar) = create_current_graphs(data)
            
            # df2 = px.data.election() # replace with your own data source
            # geojson = px.data.election_geojson()
            # fig = px.choropleth(
            #     df2, geojson=geojson, 
            #     locations="district", featureidkey="properties.district",
            #     projection="mercator", range_color=[0, 6500])
            # fig.update_geos(fitbounds="locations", visible=False)
            # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            
          
            return (gender_graph, pat_age_bar, diag_bar, proc_bar, CCI_bw, proc_revision_pie, tob_use_bar, discharge_distr_pie, comorb_bar)
        
        except:
            return ('', '','','','','','', '', '')
    else:
        return ('', '','','','','','', '', '')
        

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