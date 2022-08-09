#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 09:58:07 2022

@author: kbdetels
"""

import pandas as pd
import plotly.express as px


def pat_glance_info(df):
    
    # THESE ARE THE GENDER RATIO VARIABLES

    AJRRPat_total = len(list(df['Sex'])) # int of total patients on the spreadsheet

    males_patients = list(df['Sex'] == 'M')

    #find the indeces  of the males in the data column

    males = list(filter(lambda i: males_patients[i], range(len(males_patients))))

    males_ratio = round((len(males) / (AJRRPat_total) *100)) #% of men on the spreadsheet

    female_ratio = (100 - males_ratio)
    
    BMI_total = round((703 * (df['WeightOz']*0.0625) / (df['HeightIn'])**2).mean())

    #avergae length of stay, aka the average of the column named Lenght of Stay

    avg_length_of_stay = round(df["Length of Stay"].mean())
    
    avg_pat_age = round(df['Pat_age'].mean())
    
    return (AJRRPat_total, males_ratio, female_ratio, avg_length_of_stay, BMI_total, avg_pat_age)




def create_current_graphs(df):

    df_race =  df['PatientRaceDSC'].value_counts().to_frame(name='PatientsRace')
    
    pat_race_bar = px.bar(df_race, y = 'PatientsRace', title = 'Racial Distribution of Patients', labels = {"index" : "Race", "Patients" : "Number of Patients"},
                      color_discrete_sequence=(['darkblue']))
    
    df_eth =df['EthnicGroupDSC'].value_counts().to_frame(name = 'PatientsEth')
    
    pat_eth_bar = px.bar(df_eth, y = 'PatientsEth', title = 'Ethnical Distribution of Patients', labels = {"index" : "Ethnicity", "Patients" : "Number of Patients"},
                     color_discrete_sequence=(['darkturquoise']))
                        
    df_age = df['Pat_age'].value_counts().to_frame(name = "Patient's Age")
    pat_age_bar = px.bar(df_age, y = "Patient's Age", title = 'Age Distribution Amongst Patients', labels = {'index':'Age', "Patient's Age": "Patient's Age"},
                         color_discrete_sequence=(['Blue']))
    #Distribution of Procedures
    
    #proc_distr_pie = px.pie(df['ShortDSC'], names = df['ShortDSC'], title = "Distribution of Procedures", color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    
                                        #'lightblue', 'skyblue', 'steelblue', 'mediumblue'))
                                        
    #Remove TREAT THIGH FRACTURE, INSERT/REMOVE DRUG IMPLANT DEVICE, CPTR-ASST DIR MS PX, and TREAT HIP DISLOCATION
    # from the dataset
    searchfor = ['TREAT', 'DRUG IMPLANT DEVICE', 'CPTR']
    df_clean = df[~df['ShortDSC'].str.contains('|'.join(searchfor))]
    df_prim_rev = df_clean.copy()

    #Label all revisions as REVISION    
    df_prim_rev.loc[df_prim_rev['ShortDSC'].str.contains('REVIS'), 'ShortDSC'] = 'REVISION'
    df_prim_rev.loc[df_prim_rev['ShortDSC'].str.contains('REMOVAL'), 'ShortDSC'] = 'REVISION'
    df_prim_rev.loc[df_prim_rev['ShortDSC'].str.contains('PARTIAL'), 'ShortDSC'] = 'REVISION'



    proc_distr_pie = px.pie(df_prim_rev['ShortDSC'], names = df_prim_rev['ShortDSC'], title = "Distribution of Procedures", color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    
                                        'lightblue', 'skyblue', 'steelblue', 'mediumblue'))
    
    #Parse only revision data
    df_rev = df_clean[~df_clean['ShortDSC'].str.contains('TOTAL')]
    
    proc_revision_pie = px.pie(df_rev['ShortDSC'], names = df_rev['ShortDSC'], title = "Distribution of Revision Procedures", color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    
                                        'lightblue', 'skyblue', 'steelblue', 'mediumblue'))
    
    
    
    hip_related_CPTs = df_clean['ShortDSC'].str.contains('HIP')
    
    df_hip_related_CPTs = df_clean[hip_related_CPTs]
    
    df_hip_shortDSC = df_hip_related_CPTs['ShortDSC'].value_counts().to_frame(name='value_counts')
    
    hip_distr_bar = px.bar(df_hip_shortDSC, y = 'value_counts', title = 'Distribution of Hip Procedures',
    
                labels = {"index": "Procedure Type", "value_counts": "Number of Procedures"},  color_discrete_sequence=(['rosybrown']))
    
    
    knee_related_CPTs = df['ShortDSC'].str.contains('KNEE')
    
    df_knee_related_CPTs = df[knee_related_CPTs]
    
    df_knee_shortDSC = df_knee_related_CPTs['ShortDSC'].value_counts().to_frame(name='value_counts')
    
    
    
    knee_distr_bar = px.bar(df_knee_shortDSC, y = 'value_counts', title = 'Distribution of Knee Procedures',
    
                labels = {"index": "Procedure Type", "value_counts": "Number of Procedures"},  color_discrete_sequence=(['plum']))
    
   
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
    
    
    discharge_distr_pie = px.pie(df['DischargeDispositionDSC'], names = df['DischargeDispositionDSC'], title = "Discharge Disposition Distribution",
                     color_discrete_sequence=('powderblue', 'lightsteelblue', 'lightskyblue', 'teal', 'turquoise', 'aquamarine', 'aqua', 'lightcyan'))
    
    financial_pie = px.pie(df['OriginalFinancialClassDSC'], names=df['OriginalFinancialClassDSC'], title = ('Financial data distribution'),  
    
                           color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    
                                                    'skyblue', 'steelblue'))
    
    
    
    revenue_location_pie = px.pie(df['RevenueLocationNM'], names = df["RevenueLocationNM"], title = ('Revenue Based on Locations'),
    
                                  color_discrete_sequence=('wheat', 'burlywood', 'tan', 'rosybrown', 'goldenrod', 'peru', 'saddlebrown', 'sienna',
    
                                                    'maroon'))
    
    df_provider = df['ProviderSpecialtyDSC'].value_counts().to_frame(name='value_counts')

    provider_specialty_bar = px.bar(df_provider, y = 'value_counts', title = "Provider Specialties Based Distribution", color_discrete_sequence=(['skyblue']))
    
    
    df_hip_diag = df_hip_related_CPTs['ICD_DSC_1'].value_counts().to_frame(name='value_counts')
    
    hip_diag_bar = px.bar(df_hip_diag, y = 'value_counts' ,title = 'Hip Diagnoses', color_discrete_sequence=(['darkblue']))

    
    #hip_diag_pie = px.pie(df_hip_related_CPTs['ICD_DSC_1'], names = df_hip_related_CPTs['ICD_DSC_1'], title = 'Hip Diagnoses', color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    
     #                                               'skyblue', 'steelblue'))
    
    df_knee_diag = df_knee_related_CPTs['ICD_DSC_1'].value_counts().to_frame(name='value_counts')
    
    #knee_diag_pie = px.pie(df_knee_related_CPTs['ICD_DSC_1'], names=df_knee_related_CPTs['ICD_DSC_1'],title = 'Knee Diagnoses', color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    
     #                                               'skyblue', 'steelblue'))
     
    knee_diag_bar = px.bar(df_knee_diag, y = 'value_counts' ,title = 'Knee Diagnoses', color_discrete_sequence=(['darkblue']))

    df_BMI= df['BMI'].value_counts().to_frame(name = 'Patients')
    
   # bmi_bar = px.bar(df_BMI, y = 'Patients', title = "BMI Distribution of Patients", labels = {'index': 'BMI', 'Patients': 'Patients'}, 
    #                 color_discrete_sequence=(['#008E97'])) 
    bmi_bar = px.histogram(df['BMI'], x = 'BMI', range_x=[10,60], nbins=100)
    bmi_bar.update_layout(bargap=0.2)
    
    return (proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar, ICD10_bar, discharge_distr_pie, financial_pie, revenue_location_pie, provider_specialty_bar, pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, pat_age_bar, bmi_bar)




