# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 17:07:07 2023

@author: alucaciu and kbdetels
"""
from dash import dash_table
import pandas as pd
import plotly.express as px
import statistics
import numpy as np
from datetime import date
import time
def nongraph(all_data):
    
    #find total procedures
    total_proc = len(all_data.drop_duplicates())

    #find the total patients
    total_pat = len(all_data[['PatDOB', 'PatFirstName', 'PatLastName']].drop_duplicates())
    
    ## find out the difference in the time
    all_data.PROMs_Date = pd.to_datetime(all_data.PROMs_Date)
    ## exclude the data that has "NR" under ProcedureDate
    all_data = all_data[all_data.ProcedureDate != 'NR']
    
    ## find out how many preop, postop and linked proms were filled out 
    all_data.ProcedureDate = pd.to_datetime(all_data.ProcedureDate)
    all_data['PROMs_Date'] = all_data['PROMs_Date'].fillna('NR')    
    all_data['PROMsTimeDelta'] = (all_data.PROMs_Date[all_data.PROMs_Date != 'NR'] - all_data.ProcedureDate).dt.days
    if all_data['PROMsTimeDelta'].notna().all():
        all_data = all_data[((all_data['PROMsTimeDelta'] >= -90) & (all_data['PROMsTimeDelta'] < 456)) ]
    preop_proms_pts = round(len(all_data[all_data.PROMsTimeDelta <= 0].drop_duplicates(subset = ['PatientID']))/(len(all_data.PatientID.drop_duplicates()))*100)
    postop_proms_pts = round(len(all_data[all_data.PROMsTimeDelta > 0].drop_duplicates(subset = ['PatientID']))/(len(all_data.PatientID.drop_duplicates()))*100)
    # finding the linked ones: both preop and postop
    grouped =all_data.groupby('PatientID')
    people_with_both = 0
    for name, group in grouped:
        if any(group['PROMsTimeDelta'] > 0) and any(group['PROMsTimeDelta'] <= 0):
            people_with_both +=1
    bothproms_final = round(people_with_both/len(all_data.PatientID.drop_duplicates())*100)

    ## finding the proms filled out per person
    filtered_dates= all_data.dropna(subset=['PROMsTimeDelta'])
    pre_op_dates= filtered_dates[filtered_dates['PROMsTimeDelta'] <=0].groupby('PatientID')['PROMsTimeDelta'].count()
    post_op_dates = filtered_dates[filtered_dates['PROMsTimeDelta'] > 0].groupby('PatientID')['PROMsTimeDelta'].count()
    preop_proms_perpt = pre_op_dates.mean()
    postop_proms_perpt = post_op_dates.mean()
    
    
    return (total_proc, total_pat, preop_proms_pts, postop_proms_pts, preop_proms_perpt, postop_proms_perpt, bothproms_final)


def create_time_ind_graphs(all_data):
    
    df_his = all_data[['Surg_date', 'Main_CPT_category', 'SurName']]
    year = df_his.Surg_date.str[: 4]
    df_his = df_his.assign(year=year)

    df_rev = df_his[df_his.Main_CPT_category.str.contains('|'.join(['Revision','Explantation']))]

    df_count = df_his.year.value_counts().to_frame(name='Number of Procedures')
    df_rev_count = df_rev.year.value_counts().to_frame(name='Number of Revisions')
    counts = df_count.join(df_rev_count)
    counts['Revision Rate (%)'] = round(counts['Number of Revisions'] / counts['Number of Procedures'] * 100, 2)

    counts = counts[:3]
    counts = counts.sort_index()

    rev_count_line = px.line(counts, x= ['2019','2020','2021'], y='Revision Rate (%)',
                             color_discrete_sequence=(['crimson']),
                             markers=True, labels={'x': 'Year'},
                             range_y=[0,50])
    
    
    return (rev_count_line)



def create_current_graphs(all_data, dateless_data, start_date, end_date):

    # #Patient's Age
    all_data['PatDOB'] = pd.to_datetime(all_data['PatDOB'])
    current_date = pd.Timestamp(date.today())
    all_data['Pat_age'] = (current_date - all_data['PatDOB']).astype('<m8[Y]')
    df_age = all_data[all_data['Pat_age'] >= 65]['Pat_age'].value_counts().reset_index()
    df_age.columns = ['Age', 'Number of Patients']
    pat_age_bar = px.bar(df_age, y = "Number of Patients", 
                            labels = {'index':'Age', "Number of patients": "Number of Patients"},
                            color_discrete_sequence=(['#A70F15']))
   
    #gender distribution graph
    gender_graph = px.pie(all_data.PatSex, names = all_data.PatSex, 
                          color_discrete_sequence=(['#77030F', '#D52121']))

    
    return (pat_age_bar, gender_graph)

    