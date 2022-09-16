#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 09:58:07 2022

@author: kbdetels
"""
from dash import dash_table
import pandas as pd
import plotly.express as px


def pat_glance_info(all_data):
    
    AJRRPat_total = len(all_data) # int of total patients on the spreadsheet

    male_patients = all_data[all_data.PatSex == 'Male']

    male_ratio = round((len(male_patients) / (AJRRPat_total) *100)) #% of men on the spreadsheet

    female_ratio = (100 - male_ratio)

    BMI_total = round(all_data.Pat_bmi.mean())

    #avergae length of stay, aka the average of the column named Lenght of Stay
    avg_length_of_stay = round(all_data.Len_stay.mean())

    avg_pat_age = round(all_data.Pat_age.mean())

    
    med_CCI = all_data.CCI.median()

    return (AJRRPat_total, male_ratio, female_ratio, avg_length_of_stay, BMI_total, avg_pat_age, med_CCI)




def create_current_graphs(all_data):


    #Race data and graph
    df_race = all_data.PatRace.value_counts().to_frame(name='Number of patients')
    pat_race_bar = px.bar(df_race, y = 'Number of patients', title = 'Racial Distribution of Patients', labels = {"index" : "Race", "Patients" : "Number of Patients"},
                      color_discrete_sequence=(['darkblue']))
    #Ethnicity data and graph
    df_eth = all_data.PatEth.value_counts().to_frame(name = 'Number of patients')
    pat_eth_bar = px.bar(df_eth.head(10), y = 'Number of patients', title = 'Ethnical Distribution of Patients: Top 10', labels = {"index" : "Ethnicity", "Patients" : "Number of Patients"},
                     color_discrete_sequence=(['darkturquoise']))
    #Patient's Age
    df_age = all_data.Pat_age.value_counts().to_frame(name = "Number of patients")
    pat_age_bar = px.bar(df_age, y = "Number of patients", title = 'Age Distribution Amongst Patients', labels = {'index':'Age', "Number of patients": "Number of patients"},
                         color_discrete_sequence=(['Blue']))

    #Distribution of procedures
    proc_distr_pie = px.pie(all_data.Main_CPT_category, names = all_data.Main_CPT_category, title = "Distribution of Procedures", color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
                                        'lightblue', 'skyblue', 'steelblue', 'mediumblue'))
                                
    #Parse only revision data
    rev_data = all_data[all_data.Main_CPT_category.str.contains('Revision')]
    proc_revision_pie = px.pie(rev_data.CPT_category, names = rev_data.CPT_category, title = "Distribution of Revision Procedures", color_discrete_sequence=('wheat', 'burlywood', 'tan', 'rosybrown', 'goldenrod', 'peru', 'saddlebrown', 'sienna','maroon'))
    
    
    #Hip related CPT codes and description
    hip_data = all_data[all_data.Main_CPT_category.str.contains('Hip')]
    hip_distr_bar = px.bar(hip_data.CPT_category.value_counts().to_frame(name='value_counts'), y = 'value_counts', title = 'Distribution of Hip Procedures',
                labels = {"index": "Procedure Type", "value_counts": "Number of Procedures"},  color_discrete_sequence=(['rosybrown']))
    
    #Knee related CPT codes and descriptions
    knee_data = all_data[all_data.Main_CPT_category.str.contains('Knee')]  
    knee_distr_bar = px.bar(knee_data.CPT_category.value_counts().to_frame(name='value_counts'), y = 'value_counts', title = 'Distribution of Knee Procedures',
                            labels = {"index": "Procedure Type", "value_counts": "Number of Procedures"},  color_discrete_sequence=(['plum']))
    
    df = all_data.copy()
    
    
   #Top 10 ICD codes
    ICD_data = {'Acute_MI_ICD10': [sum(all_data.Acute_MI_ICD10.value_counts())],

               'CHF_ICD10' : [sum(all_data.CHF_ICD10.value_counts())],

               'Peripheral_vascular_disease_ICD10': [sum(all_data.Peripheral_vascular_disease_ICD10.value_counts())],

               'CVA_ICD10' : [sum(all_data.CVA_ICD10.value_counts())],

               'Dementia_ICD10' :[sum(all_data.Dementia_ICD10.value_counts())],

               'Pulmonary_disease_ICD10' :[ sum(all_data.Pulmonary_disease_ICD10.value_counts())],

               'Connective_tissue_disorder_ICD10' :[ sum(all_data.Connective_tissue_disorder_ICD10.value_counts())],

               'Peptic_ulcer_ICD10' : [sum(all_data.Peptic_ulcer_ICD10.value_counts())],

               'Liver_disease_ICD10' : [sum(all_data.Liver_disease_ICD10.value_counts())],

               'Diabetes_ICD10' : [sum(all_data.Diabetes_ICD10.value_counts())],

               'Diabetes_complications_ICD10' : [sum(all_data.Diabetes_complications_ICD10.value_counts())],

               'Paraplegia_ICD10' : [sum(all_data.Paraplegia_ICD10.value_counts())],

               'Renal_disease_ICD10':[ sum(all_data.Renal_disease_ICD10.value_counts())],

               'Cancer_ICD10' : [sum(all_data.Cancer_ICD10.value_counts())],

               'Metastatic_cancer_ICD10' : [sum(all_data.Metastatic_cancer_ICD10.value_counts())],

               'Severe_liver_disease_ICD10' : [sum(all_data.Severe_liver_disease_ICD10.value_counts())],

               'HIV_ICD10' : [sum(all_data.HIV_ICD10.value_counts())],

               'Osteoporosis_ICD10' : [sum(all_data.Osteoporosis_ICD10.value_counts())],

               'Mental_and_behavioral_disorders_due_to_psychoactive_substance_abuse_ICD10' : [sum(all_data.Mental_and_behavioral_disorders_due_to_psychoactive_substance_abuse_ICD10.value_counts())],

               'Schizophrenia_schizotypal_delusional_and_other_nonmood_disorders_ICD10' : [sum(all_data.Schizophrenia_schizotypal_delusional_and_other_nonmood_disorders_ICD10.value_counts())],

               'Mood_affective_disorders_ICD10' :[ sum(all_data.Mood_affective_disorders_ICD10.value_counts())],

               'Anxiety_dissociative_stressrelated_somatoform_and_other_nonpsychotic_mental_disorders_ICD10' : [sum(all_data.Anxiety_dissociative_stressrelated_somatoform_and_other_nonpsychotic_mental_disorders_ICD10.value_counts())],

               'PULMONARY_EMBOLISM_ACUTE_ICD10' : [sum(all_data.PULMONARY_EMBOLISM_ACUTE_ICD10.value_counts())],

               'PULMONARY_EMBOLISM_CHRONIC_ICD10' : [sum(all_data.PULMONARY_EMBOLISM_CHRONIC_ICD10.value_counts())],

               'ACUTE_DVT_LOWER_EXTREMITY_ICD10' :[ sum(all_data.ACUTE_DVT_LOWER_EXTREMITY_ICD10.value_counts())],

               'CHRONIC_DVT_LOWER_EXTREMITY_ICD10' :[ sum(all_data.CHRONIC_DVT_LOWER_EXTREMITY_ICD10.value_counts())],

               'ACUTE_DVT_UPPER_EXTREMITY_ICD10' :[ sum(all_data.ACUTE_DVT_UPPER_EXTREMITY_ICD10.value_counts())],

               'CHRONIC_DVT_UPPER_EXTREMITY_ICD10' : [sum(all_data.CHRONIC_DVT_UPPER_EXTREMITY_ICD10.value_counts())],

               'PHLEBITIS_AND_THROMBOPHLEBITIS_OF_LOWER_EXTREMITY_ICD10' : [sum(all_data.PHLEBITIS_AND_THROMBOPHLEBITIS_OF_LOWER_EXTREMITY_ICD10.value_counts())],

               'PHLEBITIS_AND_THROMBOPHLEBITIS_OF_UPPER_BODY_OR_EXTREMITY_ICD10' :[ sum(all_data.PHLEBITIS_AND_THROMBOPHLEBITIS_OF_UPPER_BODY_OR_EXTREMITY_ICD10.value_counts())],

               'UNSPECIFIED_PHLEBITIS_AND_THROMBOPHLEBITIS_ICD10' :[ sum(all_data.UNSPECIFIED_PHLEBITIS_AND_THROMBOPHLEBITIS_ICD10.value_counts())]}


    df_ICD = pd.DataFrame.from_dict(ICD_data, columns=['Comorbidity'], orient='index')

    #find the top 10 highest numbers
    
    ICD10_bar = px.bar(df_ICD.head(10).sort_values(by = 'Comorbidity',ascending = False), title = 'Top 10 Most Common ICD10 Comorbidities',
    
                       labels={'index': 'Types of Comorbidities', 'value':'Frequency'}, color ='value',  color_continuous_scale = 'ice')
    
    
    #Parse discharge distribution data
    #TODO: The difference descriptions seem to refer to different discharges so hesitant to lump together into bigger categories 
    discharge_distr_pie = px.pie(all_data.Disch_distr, names = all_data.Disch_distr, title = "Discharge Disposition Distribution",
                     color_discrete_sequence=('powderblue', 'lightsteelblue', 'lightskyblue', 'teal', 'turquoise', 'aquamarine', 'aqua', 'lightcyan'))
    
    ##Financial data - who pays for the patient's care
    #financial_pie = px.pie(df['gensurgcomorb.OriginalFinancialClassDSC'], names=df['gensurgcomorb.OriginalFinancialClassDSC'], title = ('Financial data distribution'),  
    #                       color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    #                                                'skyblue', 'steelblue'))
    
    #Provider data and graph: who are providing for the patient's procedures
    #df_provider = df['gensurgcomorb.ProviderSpecialtyDSC'].value_counts().to_frame(name='value_counts')
    #provider_specialty_bar = px.bar(df_provider, y = 'value_counts', title = "Provider Specialties Based Distribution", color_discrete_sequence=(['skyblue']))
    
    #Hip diagnoses
    all_hip_data = all_data[all_data.Main_CPT_category.str.contains('Hip')]
    df_hip_diag = all_hip_data.DX_Main_Category.value_counts().to_frame(name='Number of patients')
    #hip_diag_pie = px.pie(df_hip_related_CPTs['ICD_DSC_1'], names = df_hip_related_CPTs['ICD_DSC_1'], title = 'Hip Diagnoses', color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    #    
    hip_diag_bar = px.bar(df_hip_diag.head(10), y = 'Number of patients', title = 'Hip Diagnoses',  labels = {"index": "Diagnosis Type"},
                          color_discrete_sequence=(['darkblue']))
    
    #Knee Diagnoses
    all_knee_data = all_data[all_data.Main_CPT_category.str.contains('Knee')]
    df_knee_diag = all_knee_data.DX_Main_Category.value_counts().to_frame(name='Number of patients')
    #knee_diag_pie = px.pie(df_knee_related_CPTs['ICD_DSC_1'], names=df_knee_related_CPTs['ICD_DSC_1'],title = 'Knee Diagnoses', color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    #                                               'skyblue', 'steelblue'))
    knee_diag_bar = px.bar(df_knee_diag.head(10), y = 'Number of patients' ,title = 'Knee Diagnoses', labels = {"index": "Diagnosis Type"},
                           color_discrete_sequence=(['darkblue']))


    #Patients' BMI data
    bmi_bar = px.histogram(all_data.Pat_bmi, x = 'Pat_bmi', title='Patient BMI Distribution',
                           range_x=[0,80], nbins=100, labels={'Pat_bmi':'BMI'})
    bmi_bar.update_layout(bargap=0.2, yaxis_title='Number of patients') 
    
    #make a box and whiskers plot for BMI as 
    bmi_bw = px.box(all_data, x= 'Pat_bmi', color = 'PatSex', color_discrete_sequence =['rgb(237, 179, 20)', 'rgb(116, 161, 97)'], labels=({'Pat_bmi': 'BMI'}) )
    """
    tableBMI = dash_table.DataTable(
                                 round(all_data.Pat_bmi).to_dict('Pat_bmi'), [{'name':i, 'id': i} for i in df.columns], id='tbl1'
                            )
    
   
    #find the distribution of diagnosis - overall categories
    df_diag_count = df_diag['Category'].value_counts().to_frame(name = 'count per category')
    diag_gen_bar = px.bar(df_diag_count, y = 'count per category',title = 'Distribution of General Surgeon Diagnoses', 
                          color_discrete_sequence = (["DarkOliveGreen"]))
    """
    
    df_alc_temp = all_data.AlcoholDrinksPerWeekCNT.value_counts().to_frame(name = 'Number of Patients')
    alc_use_bar = px.bar(df_alc_temp, y = 'Number of Patients', labels = {'index': 'Number of Drinks'}, title = 'Distribution of Patients Alcoholic Drinks Consumption Per Week',
                         color_discrete_sequence=(['#966fd6']), range_x = [0, 15])
    
    """
    alc_use_type_pie = px.pie(all_data.HistoryOfDrinkTypesCD, names=(all_data.HistoryOfDrinkTypesDSC), title = 'Type of Alcoholic Drink Consumed by Patients',
                              color_discrete_sequence=(['#93ccea', '#e0ffff', '#acace6', '#b768a2']))
    """
    
    tob_use = all_data.TobUse.value_counts().to_frame(name = 'Number of patients')
    tob_use_bar = px.bar(tob_use, y = 'Number of patients', labels = {'index': 'Tobacco Use'},title = 'Distribution of Patient Tobacco Use',
                         color_discrete_sequence=(['#966fd6']))
    
    """
    return (proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar, ICD10_bar, discharge_distr_pie, financial_pie, revenue_location_pie, provider_specialty_bar,
            pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, pat_age_bar, bmi_bar, diag_gen_bar, alc_use_bar, alc_use_type_pie, tableBMI)
    """
    
    #Adding a CCI box and whiskers plot
    CCI_bw = px.box(all_data, x= 'CCI', color='PatSex', color_discrete_sequence=['rgb(237, 179, 20)', 'rgb(116, 161, 97)'], labels={'CCI': 'Charlson Comorbidity Index'})
    
    return (proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar, discharge_distr_pie, 
            pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, pat_age_bar, bmi_bar, alc_use_bar, tob_use_bar, bmi_bw, ICD10_bar, CCI_bw)
    