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
                  html.H2('''Please log in to continue:''', id='h1'),
                  dcc.Input(placeholder='Enter your username',
                            type='text', id='uname-box'),
                  dcc.Input(placeholder='Enter your password',
                            type='password', id='pwd-box'),
                  html.Button(children='Login', n_clicks=0,
                              type='submit', id='login-button'),
                  html.Div(children='', id='output-state'),
                  html.Br(),dcc.Link('Home', href='/')])
# Successful login screen
success = html.Div([html.Div([html.H2('Login successful.'),
                              html.Br(),
                              dcc.Link('Home', href='/')])  # end div
                    ])  # end div
# Failed Login
failed = html.Div([html.Div([html.H2('Log in Failed. Please try again.'),
                             html.Br(),
                             html.Div([login]),
                             dcc.Link('Home', href='/')
                             ])  # end div
                   ])  # end div
# Logout screen
logout = html.Div([html.Div(html.H2('You have been logged out - Please login')),
                   html.Br(),
                   dcc.Link('Home', href='/')
                   ])  # end div
####


# Callback function to login the user, or update the screen if the username or password are incorrect

@app.callback(
    Output('url_login', 'pathname'), Output('output-state', 'children'), [Input('login-button', 'n_clicks')], [State('uname-box', 'value'), State('pwd-box', 'value')])
def login_button_click(n_clicks, username, password):
    USER_LIST = {
        "orthobros": "orthogals",
        "god": "",
        "bardiya": "",
        "andreea": "",
        "karina": "",
        "guest": "thisissocool",
        "kelsey": " ",
    }
    
    # we need this to account for empty pass code
    password = '' if password == None else password
    
    # Check the pass and go to the next page
    if n_clicks > 0:
        try:
            if USER_LIST[username] == password:
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
    html.Br(),
    html.Hr(),
    html.Br(),
    html.Div(id='page-content'),
])


index_page = html.Div([
    dcc.Link('MGB Dashboard', href='/page-1'),
    html.Br(),
    dcc.Link('Models Page', href='/page-2'),
])


PATHS = {
    'data_aaos' : os.path.join('data','aaos_database')
   
   
    }

df = pd.read_excel(os.path.join(PATHS['data_aaos'], 'Deidentified_2021_AJRR_General_SurgeriesWithComorbidities.xlsx'), dtype={'ID':str})
#print(df.head(10))

# dropdown gets populated with this list
#surgeon_dropdown_names = list(df['Primary Surgeon'].unique())

##First row in the layout
first_row_content = html.Div([
                            
                            ], style={'backgroundColor': 'rgb(220, 248, 285)'})

##Second row in the layout
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



second_row_content =  html.Div([
                            html.H4(children =' Your Patient Information At A Glance', style={'text-align': 'center'}),
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

##Third row in the layout
#creating the figure to show in this second row
usmap = px.choropleth(df, locations= 'LocationID', locationmode='USA-states', color= (df['LocationID']), ####FIX THE RANGE THING IS WRONG
                        scope= 'usa', labels={ 'color' :'number of patients'},
                        color_continuous_scale=('Viridis'), title = ('Total Number of Procedures by State'))

financial_pie = px.pie(df['OriginalFinancialClassDSC'], names=df['OriginalFinancialClassDSC'], title = ('Financial data distribution:'))
# timelineDic = {'Mon': ['Meeting with Dr. Weber', 'Clinic'], 'Tue': ['Surgery', 'Clinic'], 'Wed': 'NA',
#                'Thr': ['Clinic', 'Lecture'], 'Fri':['Surgery', 'EOW Meeting']}
# your_timelines = px.timeline(data_frame = timelineDic, x_start = "Mon", x_end= "Fri", )


third_row_content = html.Div([
                            ###the div below contains the row with the US map and pie chart
                            html.Div([
                                    dcc.Graph(figure= usmap),
                                    ], style={'width': '50%','display': 'inline-block'}
                                    ),
                            html.Div([
                                    html.Div([
                                            dcc.Graph(figure= financial_pie)
                                            ])
                                    ], style={'width': '50%', 'display': 'inline-block'})
                            ])

##Fourth row in the layout
fourth_row_content = html.Div([
                              html.Div([
                                      html.H2([
                                          "Patient Data"
                                              ])
                                      ], style={'width': '100%', 'display': 'inline-block', 'text-align' : 'center'})
                              ], style={'backgroundColor': 'rgb(220, 248, 285)', 'display': 'inline-block', 'padding': '10px 10px', 'width':'100%'})

##Fifth row in the layout
#making the bar graphs for the two columns in the fifth row
# provider_specialty_bar = px.bar(df, x= 'ProviderSpecialtyDSC', y = df['ProviderSpecialtyDSC'].value_counts().values, width=(600), height = (500))
# df_new = df['DischargeDispositionDSC'].value_counts().to_frame(name='value_counts')
df_provider = df['ProviderSpecialtyDSC'].value_counts().to_frame(name='value_counts')

provider_specialty_bar = px.bar(df_provider, y = 'value_counts', width=(1000), height = (500), title = "Provider Specialties Based Distribution")

discharge_distr_pie = px.pie(df['DischargeDispositionDSC'], names = df['DischargeDispositionDSC'], title = "Discharge Disposition Distribution", width=(1000), height = (500))


fifth_row_content = html.Div([
                            html.Div([
                                    dcc.Graph(figure = provider_specialty_bar)
                                    ], style={'width': '50%','display': 'inline-block'}),
                             html.Div([
                                    dcc.Graph(figure = discharge_distr_pie)
                                    ], style={'width': '50%','display': 'inline-block'})
                            ])


##Sixth row in the layout

#df_discharge_distr = df['DischargeDispositionDSC'].value_counts().to_frame(name='counts')
# print(df_discharge_distr)
# print(type(df_discharge_distr))

sixth_row_content = html.Div([
                            # html.Div([
                            #         dcc.Graph(figure = discharge_distr_pie)
                            #         ], style={'width': '50%','display': 'inline-block'})
                            ])

##Seventh row in the layout
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
#print(ICD_data)
# print(ICD_data.keys())
# print(ICD_data.values())

df_ICD = pd.DataFrame.from_dict(ICD_data, columns=['Comorbidity'], orient='index')
#print(df_ICD)
# ICD_data_indeces = list(ICD_data.keys())

# ICD_dataFrame = pd.DataFrame(data = ICD_data, index=ICD_data_indeces)
# #find the top 10 highest numbers
ICD10_bar = ICD10_bar = px.bar(df_ICD, width=(2000), height = (2000) ,title = 'ICD10 Common Comorbidities', labels={'index': 'Types of Comorbidities', 'value':'Frequency'})


seventh_row_content = html.Div([
                            html.Div([
                                    dcc.Graph(figure = ICD10_bar)
                                    ], style={'width': '50%','display': 'inline-block'})
                            ])



page_1_layout = html.Div([
            html.Div([
                html.H3("Analytics Dashboard"),
                ], style={'textAlign': 'center'}),
                ##
                # make a new dataframe for visualization
# df_surgeon = df.copy(deep=True)
# # dropdown callback reads this
# dropdown_id = 0
# df_viz = df_surgeon[df_surgeon['Primary Surgeon'] == surgeon_dropdown_names[dropdown_id]]
# print(df_viz['Primary Surgeon'].head(10)
        first_row_content,
        second_row_content,
        third_row_content,
        fourth_row_content,
        fifth_row_content,
        sixth_row_content,
        seventh_row_content,
        html.Br(),
        dcc.Link('Go back to home', href='/')
])





@app.callback(Output('page-1-content', 'children'),
              [Input('page-1-dropdown', 'value')])
def page_1_dropdown(value):
    return 'You have selected "{}"'.format(value)





########################## START: PAGE 2
# page_2_layout = html.Div([
    # html.H1('Page 2'),
    # dcc.RadioItems(
        # id='page-2-radios',
        # options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
        # value='Orange'
    # ),
    # html.Div(id='page-2-content'),
    # html.Br(),
    # dcc.Link('Go to Page 1', href='/page-1'),
    # html.Br(),
    # dcc.Link('Go back to home', href='/')
# ])


page_2_layout = html.Div([
                    html.Div(className='container',
                      children=[
                                dbc.Row(html.H1("Hip Fracture Detection"), style={'textAlign': 'center'}),
                                dbc.Row(html.H1(" ")),
                                dbc.Row(
                                    html.Div([
                                            dcc.Upload(
                                                id='upload-image',
                                                children=html.Div([
                                                    'Drag and Drop or ',
                                                    html.A('Select Hip Radiographs')
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
                                            html.Div(id='output-image-upload', style={'textAlign': 'center'})
                                            ])
                                            
                                        , style={'textAlign': 'center'}),
                                ]
                        ),
                    html.Br(),
                    dcc.Link('Go to Page 1', href='/page-1'),
                    html.Br(),
                    dcc.Link('Go back to home', href='/')
                    ])





#@app.callback(Output('page-2-content', 'children'),
#              [Input('page-2-radios', 'value')])
#def page_2_radios(value):
#    return 'You have selected "{}"'.format(value)
















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
    else:
        view = index_page
    # You could also return a 404 "URL not found" page here
    return view, url








if __name__ == '__main__':
    app.run_server(debug=False)