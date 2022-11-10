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
import numpy as np

def nongraph(all_data):
    
    # all_data = all_data.drop_duplicates(subset=['PatientID','Surg_date'])
    
    total_proc = all_data['CPT_description'].count()

    BMI_total = round(all_data.Pat_bmi.mean())

    #avergae length of stay, aka the average of the column named Lenght of Stay
    avg_length_of_stay = round(all_data.Len_stay.mean())
    
    stdev_len_of_stay = round(statistics.stdev(all_data.Len_stay))
    
    avg_pat_age = round(all_data.Pat_age.mean())
    
    stdev_age = round(statistics.stdev(all_data.Pat_age))
    
    preop_proms_pts = round(all_data.AnyPROM_pre.values.sum() / len(all_data.AnyPROM_pre) * 100)
    postop_proms_pts = round(all_data.AnyPROM_post.values.sum() / len(all_data.AnyPROM_post) * 100)
    
    preop_proms_perpt = round(all_data.Preop_num.mean(),1)
    postop_proms_perpt = round(all_data.Postop_num.mean(),1)
    

    all_data.Readmit_90days = all_data.Readmit_90days.fillna(0.0)
    day90readtotal = all_data.Readmit_90days.value_counts().sum()
    
    if all_data.Readmit_90days.any(axis='rows'):
        day90read =  all_data.Readmit_90days.value_counts()[1.0]
    else:
        day90read = 0
    
    bothproms = all_data.AnyPROM_pre & all_data.AnyPROM_post
    bothproms_final = round(bothproms.values.sum() / len(bothproms) * 100)
    numbothproms = round(bothproms.values.sum())
    
    return (total_proc, avg_length_of_stay, stdev_len_of_stay, BMI_total, avg_pat_age, stdev_age, preop_proms_pts, postop_proms_pts,
            preop_proms_perpt, postop_proms_perpt, day90read, day90readtotal, bothproms_final, numbothproms)


def create_time_ind_graphs(all_data):
    
    df_his = all_data[['Surg_date', 'Main_CPT_category', 'SurName']]
    df_rev = df_his[df_his.Main_CPT_category.str.contains('|'.join(['Revision','Explantation']))]
    year = df_rev.Surg_date.str[: 4]
    df_rev = df_rev.assign(year=year)
    df_rev_count = df_rev.year.value_counts().to_frame(name='Number of Revisions')
    rev_count_line = px.line(df_rev_count, x= df_rev_count.index, y='Number of Revisions',
                             title= 'Revision Cases by Year', color_discrete_sequence=(['crimson']),
                             markers=True, labels={'index': 'Year'})
    
    
    return (rev_count_line)



def create_current_graphs(all_data, dateless_data, start_date, end_date):

    # all_data = all_data.drop_duplicates(subset=['PatientID','Surg_date'])

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
    gender_graph = px.pie(all_data.PatSex, names = all_data.PatSex, title = ' ',
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
    
    #CCI plot
    #Adding a CCI box and whiskers plot
    CCI_bw = px.box(all_data, x= 'CCI', color='PatSex', color_discrete_sequence=['#ff9999', '#dc143c'], labels={'CCI': 'Charlson Comorbidity Index', 'PatSex':'Sex'})
   
    #Parse only revision data
    rev_data = all_data[all_data.Main_CPT_category.str.contains('|'.join(['Revision','Explantation']))]
    proc_revision_pie = px.pie(rev_data.CPT_category, names = rev_data.CPT_category, title = "Distribution of Revision Procedures", color_discrete_sequence=(['Crimson']))
    

    # tableBMI = dash_table.DataTable(
    #                              round(all_data.Pat_bmi).to_dict('Pat_bmi'), [{'name':i, 'id': i} for i in df.columns], id='tbl1'
    #                         )
    
   
    # #find the distribution of diagnosis - overall categories
    # df_diag_count = df_diag['Category'].value_counts().to_frame(name = 'count per category')
    # diag_gen_bar = px.bar(df_diag_count, y = 'count per category',title = 'Distribution of General Surgeon Diagnoses', 
    #                       color_discrete_sequence = (["DarkOliveGreen"]))
    # """
    
    
    
    tob_use = all_data.TobUse.value_counts().to_frame(name = 'Number of patients')
    tob_use_bar = px.bar(tob_use, y = 'Number of patients', labels = {'index': 'Tobacco Use History'},title = 'Smoking History - Tobacco Use',
                          color_discrete_sequence=(['#8b0000']))

    #
    discharge_distr_pie = px.pie(all_data.Disch_distr, names = all_data.Disch_distr, title = "Discharge Disposition Distribution",
                     color_discrete_sequence=('#ff9999 ', '#ff6961', '#dc143c', '#ab4b52', '#cf1020', '#8b0000', '#cc6666 ', '#ea3c53',
                                        '#800000', '#ff4040', '#eb4c42', '#cd5c5c'))
    
    
    ICD_data = {'Acute MI': [sum(all_data.Acute_MI_ICD10.value_counts())],

               'CHF' : [sum(all_data.CHF_ICD10.value_counts())],

               'Peripheral Vascular Disease': [sum(all_data.Peripheral_vascular_disease_ICD10.value_counts())],

               'CVA' : [sum(all_data.CVA_ICD10.value_counts())],

               'Dementia' :[sum(all_data.Dementia_ICD10.value_counts())],

               'Pulmonary Disease' :[ sum(all_data.Pulmonary_disease_ICD10.value_counts())],

               'Connective Tissue Disorder' :[ sum(all_data.Connective_tissue_disorder_ICD10.value_counts())],

               'Peptic Ulcer' : [sum(all_data.Peptic_ulcer_ICD10.value_counts())],

               'Liver Disease' : [sum(all_data.Liver_disease_ICD10.value_counts())],

               'Diabetes' : [sum(all_data.Diabetes_ICD10.value_counts())],

               'Diabetes Complications' : [sum(all_data.Diabetes_complications_ICD10.value_counts())],

               'Paraplegia' : [sum(all_data.Paraplegia_ICD10.value_counts())],

               'Renal Disease':[ sum(all_data.Renal_disease_ICD10.value_counts())],

               'Cancer' : [sum(all_data.Cancer_ICD10.value_counts())],

               'Metastatic Cancer' : [sum(all_data.Metastatic_cancer_ICD10.value_counts())],

               'Severe Liver Disease' : [sum(all_data.Severe_liver_disease_ICD10.value_counts())],

               'HIV' : [sum(all_data.HIV_ICD10.value_counts())],

               'Osteoporosis' : [sum(all_data.Osteoporosis_ICD10.value_counts())],

               'Mental and Behavioral Disorders due to Psychoactive Substance Abuse' : [sum(all_data.Mental_and_behavioral_disorders_due_to_psychoactive_substance_abuse_ICD10.value_counts())],

               'Schizophrenia Schizotypal Delusional and Other Nonmood Disorders' : [sum(all_data.Schizophrenia_schizotypal_delusional_and_other_nonmood_disorders_ICD10.value_counts())],

               'Mood Affective Disorders' :[ sum(all_data.Mood_affective_disorders_ICD10.value_counts())],

               'Anxiety Dissociative Stress Related Somatoform and Other Nonpsychotic Mental Disorders' : [sum(all_data.Anxiety_dissociative_stressrelated_somatoform_and_other_nonpsychotic_mental_disorders_ICD10.value_counts())],

               'PULMONARY EMBOLISM ACUTE' : [sum(all_data.PULMONARY_EMBOLISM_ACUTE_ICD10.value_counts())],

               'PULMONARY EMBOLISM CHRONIC' : [sum(all_data.PULMONARY_EMBOLISM_CHRONIC_ICD10.value_counts())],

               'ACUTE DVT LOWER EXTREMITY' :[ sum(all_data.ACUTE_DVT_LOWER_EXTREMITY_ICD10.value_counts())],

               'CHRONIC DVT LOWER EXTREMITY' :[ sum(all_data.CHRONIC_DVT_LOWER_EXTREMITY_ICD10.value_counts())],

               'ACUTE DVT UPPER EXTREMITY' :[ sum(all_data.ACUTE_DVT_UPPER_EXTREMITY_ICD10.value_counts())],

               'CHRONIC DVT UPPER EXTREMITY' : [sum(all_data.CHRONIC_DVT_UPPER_EXTREMITY_ICD10.value_counts())],

               'PHLEBITIS AND THROMBOPHLEBITIS OF LOWER EXTREMITY' : [sum(all_data.PHLEBITIS_AND_THROMBOPHLEBITIS_OF_LOWER_EXTREMITY_ICD10.value_counts())],

               'PHLEBITIS AND THROMBOPHLEBITIS OF UPPER BODY OR EXTREMITY' :[ sum(all_data.PHLEBITIS_AND_THROMBOPHLEBITIS_OF_UPPER_BODY_OR_EXTREMITY_ICD10.value_counts())],

               'UNSPECIFIED PHLEBITIS AND THROMBOPHLEBITIS' :[ sum(all_data.UNSPECIFIED_PHLEBITIS_AND_THROMBOPHLEBITIS_ICD10.value_counts())]}
    
    
    
    df_ICD = pd.DataFrame.from_dict(ICD_data, columns=['Comorbidity'], orient='index')
    comorb = df_ICD.head(10)
    comorb_bar = px.bar(comorb.sort_values(by='Comorbidity', ascending = False), y = 'Comorbidity', labels = {'index': 'Types of Comorbidities', 'Comorbidity': 'Number of Cases'},title = 'Most Common 10 Comorbidities',
                          color_discrete_sequence=(['#8b0000']))
    
    
    #FIND LINKED CASES
    linked_df = dateless_data[dateless_data.duplicated('PatientID',keep=False)]
    grp = linked_df.groupby('PatientID')
    linked_revisions = pd.DataFrame()

    for PatientID, group in grp:
        
        temp = group  
        primary = temp.Main_CPT_category.str.contains('Primary').any()  
        revision = temp.Main_CPT_category.str.contains('|'.join(['Revision','Explantation'])).any()
        linked = all([primary, revision])
        
        if linked == True:
            linked_case = group[group.Main_CPT_category.str.contains('|'.join(['Revision','Explantation']))]
            linked_revisions = linked_revisions.append(linked_case)
    
    #Filter by date range
    # linked_revisions.Surg_date = pd.to_datetime(linked_revisions.Surg_date)
    # linked_revisions = linked_revisions[(linked_revisions.Surg_date > start_date) & (linked_revisions.Surg_date < end_date)] 
    
    #Graph linked cases
    # linked_pie = px.pie(linked_revisions.DX_Main_Category, names = linked_revisions.DX_Main_Category, title = "Linked Revision Burden by Diagnosis", color_discrete_sequence=(['Crimson']))
    linked_revision_counts = linked_revisions.DX_Main_Category.value_counts().to_frame(name = 'Number of patients')
    linked_bar = px.bar(linked_revision_counts, y = 'Number of patients', labels = {'index': 'DX_Main_Category', 'DX_Main_Category':'Main Diagnosis Category'},title = 'Linked Revision Burden by Diagnosis',
                          color_discrete_sequence=(['#8b0000']))
    
    
    return (gender_graph, pat_age_bar, diag_bar, proc_bar, CCI_bw, proc_revision_pie,tob_use_bar, discharge_distr_pie, comorb_bar, linked_bar)
    