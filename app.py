# Read Required Libraries
import os

from flask import Flask
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import random

## Models Libraries
import datetime
import numpy as np
from codes.util_images import im_preprocess
import cv2
import base64



#### FIXUS BEGINS
PATHS = {
    'images': os.path.join('images'),

    'data_aaos' : os.path.join('data','aaos_database')
    }

### Loading Data for MGB Dashboard
df_mgb = pd.read_excel(os.path.join(PATHS['data_aaos'], 'Deidentified_2021_AJRR_General_SurgeriesWithComorbidities.xlsx'), dtype={'ID':str})
df = pd.read_excel(os.path.join(PATHS['data_aaos'], 'Deidentified_2021_AJRR_General_SurgeriesWithComorbidities.xlsx'), dtype={'ID':str})


# CREDIT: This code is copied from Dash official documentation:
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


@ login_manager.user_loader
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
list_surgeons = pd.Series(df['Primary Surgeon']).unique().tolist()
#create username for each primary surgeon using a loop
USER_TO_NAME = {}
USER_LIST= {}
    
#print(list_surgeons)
for x in list_surgeons:
    un = []
    #print(x)
    for i in range (len(list_surgeons)):
            un =x[0] + x.rsplit(' ', 1)[1]
            USER_TO_NAME.update({str(un): x})
            USER_LIST.update({str(un) : str(x[0: 2] + x[0:2])})
    
print(USER_LIST)

@app.callback(
    Output('url_login', 'pathname'), Output('output-state', 'children'), [Input('login-button', 'n_clicks')], [State('uname-box', 'value'), State('pwd-box', 'value')])
def login_button_click(n_clicks, username, password):
    global df
    #### Creating a dict with all surgeon names and usernames
    list_surgeons = pd.Series(df['Primary Surgeon']).unique().tolist()
#create username for each primary surgeon using a loop
    USER_TO_NAME = {}
    USER_LIST= {}
    
#print(list_surgeons)
    for x in list_surgeons:
        un = []
    #print(x)
        for i in range (len(list_surgeons)):
            un =x[0] + x.rsplit(' ', 1)[1]
            USER_TO_NAME.update({str(un): x})
            USER_LIST.update({str(un) : str(x[0: 2] + x[0:2])})
    
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
app.layout = html.Div([
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





#TODO: work on the surgeon specific stuff
#TODO: work on dropdown: other surgeons can see other surgeons

##surgeon_dropdown_names = list(df['Primary Surgeon'].unique())


###LEAVE : OLD USER_TO_NAME
# USER_TO_NAME = {
#     'vivek': 'Vivek M Shah',
#     'andreea': 'Antonia F Chen'
#     }




# TODO: how to acces the username globally (the person who has logged in)

# current_user_name = username_global #

# # TODO: this is bad, we need to make this approch better

# try:

#     df_surgeon = df[df['Primary Surgeon'] == USER_TO_NAME[current_user_name]]

# except:

#     df = df.copy(deep=True)

##Info at a lance  row in the layout

#setup the variables for the AAOS data




# THESE ARE THE GENDER RATIO VARIABLES

AJRRPat_total = len(list(df['Sex'])) # int of total patients on the spreadsheet

males_patients = list(df['Sex'] == 'M')

#find the indeces  of the males in the data column

males = list(filter(lambda i: males_patients[i], range(len(males_patients))))

males_ratio = round((len(males) / (AJRRPat_total) *100)) #% of men on the spreadsheet

female_ratio = (100 - males_ratio)



#avergae length of stay, aka the average of the column named Lenght of Stay

avg_length_of_stay = round(df["Length of Stay"].mean())

# the whole blue row on the dashboard that gives

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

                                    ], style={'width':'150px', 'height':'100px', 'display': 'inline-block'})

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

                                                            html.P('-', className='card-content',

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

                                            ], style={'width':'400px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                            html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average patient BMI', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P('-', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'300px', 'height':'100px', 'display': 'inline-block'})

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

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Percent patients with comorbidities', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P('100%', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'400px', 'height':'100px', 'display': 'inline-block'})

                                    ], style={'display': 'inline-block', 'padding': '10px 10px'})

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



#row figures and variables for procedures category

df_shortDSC = df['ShortDSC'].value_counts().to_frame(name='value_counts')


# This is the pi plot
proc_distr_pie = px.pie(df['ShortDSC'], names = df['ShortDSC'], title = "Distribution of Procedures", color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',

                                                'lightblue', 'skyblue', 'steelblue', 'mediumblue'))





knee_related_CPTs = df['ShortDSC'].str.contains('KNEE')

df_knee_related_CPTs = df[knee_related_CPTs]

df_knee_shortDSC = df_knee_related_CPTs['ShortDSC'].value_counts().to_frame(name='value_counts')



knee_distr_bar = px.bar(df_knee_shortDSC, y = 'value_counts', title = 'Distribution of Knee Procedures',

                        labels = {"index": "Procedure Type", "value_counts": "Number of Procedures"},  color_discrete_sequence=(['plum']))





proc_totalAndKnee = html.Div([

                 html.Div([

                          dcc.Graph(figure = proc_distr_pie)

                          ], style={'width': '50%','display': 'inline-block'}),

                 html.Div([

                          dcc.Graph(figure = knee_distr_bar)

                          ], style={'width': '50%','display': 'inline-block'})

                ])



hip_related_CPTs = df['ShortDSC'].str.contains('HIP')

df_hip_related_CPTs = df[hip_related_CPTs]

cpt_bar = px.bar(x = df_hip_related_CPTs['CPT'].value_counts(), y= pd.Series(df_hip_related_CPTs['CPT'].unique().tolist(), dtype='str'),

                 labels={'y': 'Types of CPT Codes', 'x':'Frequency'}, color_discrete_sequence=(['rosybrown']),

                 title = 'Hip Related CPT codes')



proc_hip = html.Div([

                html.Div([

                        dcc.Graph(figure = cpt_bar)

                        ], style={'width': '50%', 'display': 'inline-block'})

                ])

## Comorbidities and complications category

comorb_info  = html.Div([

                        html.Div([

                                html.H5([

                                        "Comorbidities and complications"

                                        ])

                                ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                        ], style={'backgroundColor': 'rgb(224, 224, 255)', 'display': 'inline-block', 'width': '100%'})



ICD_data = {'Acute_MI_ICD10': [sum(df['Acute_MI_ICD10'].value_counts())],

               'CHF_ICD10' : [sum(df['CHF_ICD10'].value_counts())],

               'Peripheral_vascular_disease_ICD10': [sum(df['Peripheral_vascular_disease_ICD10'].value_counts())],

               'CVA_ICD10' : [sum(df['CVA_ICD10'].value_counts())],

               'Dementia_ICD10' :[sum(df['Dementia_ICD10'].value_counts())],

               'Pulmonary_disease_ICD10' :[ sum(df['Pulmonary_disease_ICD10'].value_counts())],

               'Connective_tissue_disorder_ICD10' :[ sum(df['Connective_tissue_disorder_ICD10'].value_counts())],

               'Peptic_ulcer_ICD10' : [sum(df['Peptic_ulcer_ICD10'].value_counts())],

               'Liver_disease_ICD10' : [sum(df['Liver_disease_ICD10'].value_counts())],

               'Diabetes_ICD10' : [sum(df['Diabetes_ICD10'].value_counts())],

               'Diabetes_complications_ICD10' : [sum(df['Diabetes_complications_ICD10'].value_counts())],

               'Paraplegia_ICD10' : [sum(df['Paraplegia_ICD10'].value_counts())],

               'Renal_disease_ICD10':[ sum(df['Renal_disease_ICD10'].value_counts())],

               'Cancer_ICD10' : [sum(df['Cancer_ICD10'].value_counts())],

               'Metastatic_cancer_ICD10' : [sum(df['Metastatic_cancer_ICD10'].value_counts())],

               'Severe_liver_disease_ICD10' : [sum(df['Severe_liver_disease_ICD10'].value_counts())],

               'HIV_ICD10' : [sum(df['HIV_ICD10'].value_counts())],

               'ALL_ICD10' : [sum(df['ALL_ICD10'].value_counts())],

               'Osteoporosis_ICD10' : [sum(df['Osteoporosis_ICD10'].value_counts())],

               'Mental_and_behavioral_disorders_due_to_psychoactive_substance_abuse_ICD10' : [sum(df['Mental_and_behavioral_disorders_due_to_psychoactive_substance_abuse_ICD10'].value_counts())],

               'Schizophrenia_schizotypal_delusional_and_other_nonmood_disorders_ICD10' : [sum(df['Schizophrenia_schizotypal_delusional_and_other_nonmood_disorders_ICD10'].value_counts())],

               'Mood_affective_disorders_ICD10' :[ sum(df['Mood_affective_disorders_ICD10'].value_counts())],

               'Anxiety_dissociative_stressrelated_somatoform_and_other_nonpsychotic_mental_disorders_ICD10' : [sum(df['Anxiety_dissociative_stressrelated_somatoform_and_other_nonpsychotic_mental_disorders_ICD10'].value_counts())],

               'PULMONARY_EMBOLISM_ACUTE_ICD10' : [sum(df['PULMONARY_EMBOLISM_ACUTE_ICD10'].value_counts())],

               'PULMONARY_EMBOLISM_CHRONIC_ICD10' : [sum(df['PULMONARY_EMBOLISM_CHRONIC_ICD10'].value_counts())],

               'ACUTE_DVT_LOWER_EXTREMITY_ICD10' :[ sum(df['ACUTE_DVT_LOWER_EXTREMITY_ICD10'].value_counts())],

               'CHRONIC_DVT_LOWER_EXTREMITY_ICD10' :[ sum(df['CHRONIC_DVT_LOWER_EXTREMITY_ICD10'].value_counts())],

               'ACUTE_DVT_UPPER_EXTREMITY_ICD10' :[ sum(df['ACUTE_DVT_UPPER_EXTREMITY_ICD10'].value_counts())],

               'CHRONIC_DVT_UPPER_EXTREMITY_ICD10' : [sum(df['CHRONIC_DVT_UPPER_EXTREMITY_ICD10'].value_counts())],

               'PHLEBITIS_AND_THROMBOPHLEBITIS_OF_LOWER_EXTREMITY_ICD10' : [sum(df['PHLEBITIS_AND_THROMBOPHLEBITIS_OF_LOWER_EXTREMITY_ICD10'].value_counts())],

               'PHLEBITIS_AND_THROMBOPHLEBITIS_OF_UPPER_BODY_OR_EXTREMITY_ICD10' :[ sum(df['PHLEBITIS_AND_THROMBOPHLEBITIS_OF_UPPER_BODY_OR_EXTREMITY_ICD10'].value_counts())],

               'UNSPECIFIED_PHLEBITIS_AND_THROMBOPHLEBITIS_ICD10' :[ sum(df['UNSPECIFIED_PHLEBITIS_AND_THROMBOPHLEBITIS_ICD10'].value_counts())]}





df_ICD = pd.DataFrame.from_dict(ICD_data, columns=['Comorbidity'], orient='index')



#find the top 10 highest numbers

ICD10_bar = px.bar(df_ICD.head(10).sort_values(by = 'Comorbidity',ascending = False), title = 'Top 10 Most Common ICD10 Comorbidities',

                               labels={'index': 'Types of Comorbidities', 'value':'Frequency'}, color ='value',  color_continuous_scale = 'ice')



comorb_ICD10Top10 = html.Div([

                html.Div([

                        dcc.Graph(figure = ICD10_bar)
                       

                        ], style={'width': '100%','display': 'inline-block'})

                ])







discharge_distr_pie = px.pie(df['DischargeDispositionDSC'], names = df['DischargeDispositionDSC'], title = "Discharge Disposition Distribution",

                             color_discrete_sequence=('powderblue', 'lightsteelblue', 'lightskyblue', 'teal', 'turquoise', 'aquamarine', 'aqua', 'lightcyan'))





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





financial_pie = px.pie(df['OriginalFinancialClassDSC'], names=df['OriginalFinancialClassDSC'], title = ('Financial data distribution'),  

                       color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',

                                                'skyblue', 'steelblue'))



revenue_location_pie = px.pie(df['RevenueLocationNM'], names = df["RevenueLocationNM"], title = ('Revenue Based on Locations'),

                              color_discrete_sequence=('wheat', 'burlywood', 'tan', 'rosybrown', 'goldenrod', 'peru', 'saddlebrown', 'sienna',

                                                'maroon'))



fin_patAndRev = html.Div([

                html.Div([

                        dcc.Graph(figure = financial_pie)

                        ], style={'width': '50%','display': 'inline-block'}),

                html.Div([

                        dcc.Graph(figure = revenue_location_pie)

                        ], style={'width': '50%','display': 'inline-block'})

                ])

##Institution information

inst_info = html.Div([

                        html.Div([

                                html.H5([

                                        "Institution Information"

                                        ])

                                ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})

                        ], style={'backgroundColor': 'rgb(224, 224, 255)', 'display': 'inline-block', 'width': '100%'})



df_provider = df['ProviderSpecialtyDSC'].value_counts().to_frame(name='value_counts')



provider_specialty_bar = px.bar(df_provider, y = 'value_counts', title = "Provider Specialties Based Distribution", color_discrete_sequence=(['skyblue']))



inst_prov = html.Div([

                            html.Div([

                                    dcc.Graph(figure = provider_specialty_bar)

                                    ], style={'width': '50%','display': 'inline-block'})

                            ])

#Surgeon related info tab

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

                                            ], style={'width':'150px', 'height':'100px', 'display': 'inline-block'})

                                        ], style={'display': 'inline-block', 'padding':'10px, 10px'}),

                                html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Institution', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P('-', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'250px', 'height':'100px', 'display': 'inline-block'})

                                        ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                                html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average patient age', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P('-', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'300px', 'height':'100px', 'display': 'inline-block'})

                                            ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                                html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Sex Ratio', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P(id='sex_ratio', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'400px', 'height':'100px', 'display': 'inline-block'})

                                        ], style={'display': 'inline-block', 'padding': '10px 10px'}),

                                html.Div([

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Average patient BMI', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P('-', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'300px', 'height':'100px', 'display': 'inline-block'})

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

                                    dbc.Card([

                                            dbc.CardBody([

                                                            html.H4('Percent patients with comorbidities', className= 'card-title',

                                                            style={'textAlign': 'center','color': '#0074D9'}),

                                                            html.P('100%', className='card-content',

                                                                   style={'textAlign':'center', 'font-family':'helvetica', 'font-size': '20px'})

                                                        ])

                                            ], style={'width':'400px', 'height':'100px', 'display': 'inline-block'})

                                        ], style={'display': 'inline-block', 'padding': '10px 10px'})

                                ], style={'backgroundColor': 'rgb(220, 248, 285)'})






#####THIS IS THE MAIN DASHBOARD PAGE LAYOUT: please don't clutter

page_1_layout = html.Div([

            dcc.Link('Go back to home', href='/'),
            html.Div([

                html.H3("Analytics Dashboard")], style={'textAlign': 'center'}),
           
            html.Div(html.H2(id='surgeon_name', children = '')),
            
            dcc.Tabs([
                    dcc.Tab(label = 'MGB Patients', children = [
                                                              pat_info_at_glance,
                                                              
                                                              html.Br(),
                                                              
                                                              pat_info_header,
                                                              
                                                              comorb_info,

                                                              comorb_ICD10Top10,
                                                              
                                                              prom_discharge,
                                                              
                                                              surg_info_header,

                                                              proc_info,

                                                              proc_totalAndKnee,

                                                              proc_hip,

                                                              inst_info_header,
                                                              
                                                              fin_patAndRev,

                                                              inst_prov  
                                                            ]),

                        dcc.Tab(label= 'Your patients', children = [
                                                                    pat_tab_glance
                                                                    
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
    #Output('num_patients','children'),
    #Output('sex_ratio','children'),
    #Output('avg_stay', 'children'),
    [Input('login-status','data')])
def update_output_div(username):
    global USER_TO_NAME
    if username in USER_TO_NAME.keys():
        try: 
            name = USER_TO_NAME[username]
            #df_surgeon = df[df['Primary Surgeon'] == USER_TO_NAME[username]]
            # AJRRPat_total = len(list(df_surgeon['Sex']))
            # AJRRPat_total_output = '{}'.format(AJRRPat_total)
            
            # males_patients = list(df_surgeon['Sex'] == 'M')
            # males = list(filter(lambda i: males_patients[i], range(len(males_patients))))
            # males_ratio = round((len(males) / (AJRRPat_total) *100)) #% of men on the spreadsheet
            # female_ratio = (100 - males_ratio)
            # sex_ratio_output = '{}% males and {}% females'.format(males_ratio, female_ratio)
            
            # avg_length_of_stay = round(df_surgeon["Length of Stay"].mean())
            # avg_stay_output = '{}'.format(avg_length_of_stay)
            
            return ('Username: {}'.format(username), 'Name: {}'.format(name)) #AJRRPat_total_output, sex_ratio_output, avg_stay_output
        except:  
            return ('','No Surgeon Specific Data')
    else:
        return ('', '')


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








if __name__ == '__main__':
    app.run_server(debug=True)