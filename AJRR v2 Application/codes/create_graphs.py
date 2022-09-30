#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 09:58:07 2022

@author: kbdetels
"""
from dash import dash_table
import pandas as pd
import plotly.express as px
import statistics

def nongraph(all_data):
    
    total_proc = all_data['CPT_description'].count()

    BMI_total = round(all_data.Pat_bmi.mean())

    #avergae length of stay, aka the average of the column named Lenght of Stay
    avg_length_of_stay = round(all_data.Len_stay.mean())
    
    stdev_len_of_stay = round(statistics.stdev(all_data.Len_stay))
    
    avg_pat_age = round(all_data.Pat_age.mean())
    
    stdev_age = round(statistics.stdev(all_data.Pat_age))
    
    med_CCI = round(all_data.CCI.mean(),2)
    
    inst = all_data.Hosp_name.values[0]

    
    return (total_proc, avg_length_of_stay, stdev_len_of_stay, BMI_total, avg_pat_age, stdev_age, med_CCI, inst)




def create_current_graphs(all_data):


    # #Race data and graph
    # df_race = all_data.PatRace.value_counts().to_frame(name='Number of patients')
    # pat_race_bar = px.bar(df_race, y = 'Number of patients', title = 'Racial Distribution of Patients', labels = {"index" : "Race", "Patients" : "Number of Patients"},
    #                   color_discrete_sequence=(['darkblue']))
    # #Ethnicity data and graph
    # df_eth = all_data.PatEth.value_counts().to_frame(name = 'Number of patients')
    # pat_eth_bar = px.bar(df_eth.head(10), y = 'Number of patients', title = 'Ethnical Distribution of Patients: Top 10', labels = {"index" : "Ethnicity", "Patients" : "Number of Patients"},
    #                  color_discrete_sequence=(['darkturquoise']))
    # #Patient's Age
    df_age = all_data.Pat_age.value_counts().to_frame(name = "Number of patients")
    # avg_pat_age = round(all_data.Pat_age.mean())
    # std_age= statistics.stdev(df_age)
    pat_age_bar = px.bar(df_age, y = "Number of patients", title = ' ',
                            labels = {'index':'Age', "Number of patients": "Number of patients"},
                            color_discrete_sequence=(['Crimson']))
    #gender distribution graph
    AJRRPat_total = len(all_data) 
    male_patients = all_data[all_data.PatSex == 'Male']
    male_ratio = round((len(male_patients) / (AJRRPat_total) *100)) #% of men on the spreadsheet
    female_ratio = (100 - male_ratio)
    gender_ratio = {'Male' : [male_ratio], 'Female' : [female_ratio]}
    gender_ratio_df = pd.DataFrame(gender_ratio)
    gender_graph = px.pie(gender_ratio_df, names=['Male', 'Female'] , title = ' ',
                          color_discrete_sequence=(['#ff9999', '#dc143c']))
    #Distribution of procedures
    proc_distr_pie = px.pie(all_data.Main_CPT_category, names = all_data.Main_CPT_category, color_discrete_sequence=('#ff9999 ', '#ff6961', '#dc143c', '#ab4b52', '#cf1020', '#8b0000', '#cc6666 ', '#ea3c53',
                                        '#800000', '#ff4040', '#eb4c42', '#cd5c5c'))
      
    #Diagnoses
    df_diag = all_data.DX_Main_Category.value_counts().to_frame(name='Number of patients')   
    diag_bar = px.bar(df_diag.head(10), y = 'Number of patients', title = ' ',  labels = {"index": "Diagnosis Type"},
                      color_discrete_sequence=(['Crimson']))
    
    
    #Procedures
    df_proc = all_data.CPT_category.value_counts().to_frame(name= 'Number of patients')
    proc_bar = px.bar(df_proc, y =  'Number of patients', title = ' ', labels={'index': 'Type of Procedure- based on CPT'}, 
                      color_discrete_sequence=(['Crimson']))
    # #Parse only revision data
    # rev_data = all_data[all_data.Main_CPT_category.str.contains('Revision')]
    # proc_revision_pie = px.pie(rev_data.CPT_category, names = rev_data.CPT_category, title = "Distribution of Revision Procedures", color_discrete_sequence=('wheat', 'burlywood', 'tan', 'rosybrown', 'goldenrod', 'peru', 'saddlebrown', 'sienna','maroon'))
    

    # tableBMI = dash_table.DataTable(
    #                              round(all_data.Pat_bmi).to_dict('Pat_bmi'), [{'name':i, 'id': i} for i in df.columns], id='tbl1'
    #                         )
    
   
    # #find the distribution of diagnosis - overall categories
    # df_diag_count = df_diag['Category'].value_counts().to_frame(name = 'count per category')
    # diag_gen_bar = px.bar(df_diag_count, y = 'count per category',title = 'Distribution of General Surgeon Diagnoses', 
    #                       color_discrete_sequence = (["DarkOliveGreen"]))
    # """
    
    # df_alc_temp = all_data.AlcoholDrinksPerWeekCNT.value_counts().to_frame(name = 'Number of Patients')
    # alc_use_bar = px.bar(df_alc_temp, y = 'Number of Patients', labels = {'index': 'Number of Drinks'}, title = 'Distribution of Patients Alcoholic Drinks Consumption Per Week',
    #                      color_discrete_sequence=(['#966fd6']), range_x = [0, 15])
    
    # """
    # alc_use_type_pie = px.pie(all_data.HistoryOfDrinkTypesCD, names=(all_data.HistoryOfDrinkTypesDSC), title = 'Type of Alcoholic Drink Consumed by Patients',
    #                           color_discrete_sequence=(['#93ccea', '#e0ffff', '#acace6', '#b768a2']))
    # """
    
    # tob_use = all_data.TobUse.value_counts().to_frame(name = 'Number of patients')
    # tob_use_bar = px.bar(tob_use, y = 'Number of patients', labels = {'index': 'Tobacco Use'},title = 'Distribution of Patient Tobacco Use',
    #                      color_discrete_sequence=(['#966fd6']))
    
    return (proc_distr_pie, gender_graph, pat_age_bar, diag_bar, proc_bar)
    