#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 09:58:07 2022

@author: kbdetels
"""
from dash import dash_table
import pandas as pd
import plotly.express as px


def pat_glance_info(df, df_mgb):
   
    ####TODO: make sure these only count per patient and not all the copies
    # THESE ARE THE GENDER RATIO VARIABLES
    
    AJRRPat_total = len(list(df['PatientID'].unique())) # int of total patients on the spreadsheet
    
    males_patients = list(df['SexDSC'] == 'Male')

    #find the indeces  of the males in the data column

    males = list(filter(lambda i: males_patients[i], range(len(males_patients))))

    males_ratio = round((len(males) / (AJRRPat_total) *100)) #% of men on the spreadsheet

    female_ratio = (100 - males_ratio)
    
    if round((703 * (df['weight.WeightOz']*0.0625) / (df['height.HeightIn'])**2).mean()) < 100:
        BMI_total = round((703 * (df['weight.WeightOz']*0.0625) / (df['height.HeightIn'])**2).mean())
    else:
        BMI_total= 'not available'
    #avergae length of stay, aka the average of the column named Lenght of Stay

    avg_length_of_stay = round(df["surgeons.Length of Stay"].mean())
    
    avg_pat_age = round(df['Pat_age'].mean())
    
    return (AJRRPat_total, males_ratio, female_ratio, avg_length_of_stay, BMI_total, avg_pat_age)




def create_current_graphs(df, df_mgb, df_diag):

    
<<<<<<< HEAD
    #Remove TREAT THIGH FRACTURE, INSERT/REMOVE DRUG IMPLANT DEVICE, CPTR-ASST DIR MS PX, and TREAT HIP DISLOCATION
    # from the dataset
    searchfor = ['TREAT', 'DRUG IMPLANT DEVICE', 'CPTR']
    df_clean = df[~df['procedures.ShortDSC'].str.contains('|'.join(searchfor))]
    df = df_clean
    
    #Parse through procedure descriptions to condense and lowercase labels
    df.loc[df['procedures.ShortDSC'].str.contains('REVISE HIP JOINT REPLACEMENT'), 'procedures.ShortDSC'] = 'Revision of Hip Joint'
    df.loc[df['procedures.ShortDSC'].str.contains('PARTIAL HIP'), 'procedures.ShortDSC'] = 'Partial Hip Replacement'
    df.loc[df['procedures.ShortDSC'].str.contains('REVISE/REPLACE KNEE JOINT'), 'procedures.ShortDSC'] = 'Revision of Knee Joint'
    df.loc[df['procedures.ShortDSC'].str.contains('REVISION OF KNEE JOINT'), 'procedures.ShortDSC'] = 'Revision of Knee Joint'
    df.loc[df['procedures.ShortDSC'].str.contains('REMOVAL OF KNEE PROSTHESIS'), 'procedures.ShortDSC'] = 'Removal of Knee Prosthesis'
    #Lowercase total knee/hip replacement labels
    df.loc[df['procedures.ShortDSC'].str.contains('TOTAL KNEE'), 'procedures.ShortDSC'] = 'Total Knee Replacement'
    df.loc[df['procedures.ShortDSC'].str.contains('TOTAL HIP'), 'procedures.ShortDSC'] = 'Total Hip Replacement'
=======
    return (AJRRPat_total, male_ratio, female_ratio, avg_length_of_stay, BMI_total, avg_pat_age)




def create_current_graphs(all_data, df_diag):
>>>>>>> parent of 96c07a8 (Removed df_diag)

    #Label all revisions as REVISION        
    df_prim_rev = df.copy()
    df_prim_rev.loc[df_prim_rev['procedures.ShortDSC'].str.contains('Revis'), 'procedures.ShortDSC'] = 'Revision'
    df_prim_rev.loc[df_prim_rev['procedures.ShortDSC'].str.contains('Removal'), 'procedures.ShortDSC'] = 'Revision'
    df_prim_rev.loc[df_prim_rev['procedures.ShortDSC'].str.contains('Partial'), 'procedures.ShortDSC'] = 'Revision'

    #Race data and graph
    df_race = df['PatientRaceDSC'].value_counts().to_frame(name='Count')
    pat_race_bar = px.bar(df_race, y = 'Count', title = 'Racial Distribution of Patients', labels = {"index" : "Race", "Patients" : "Number of Patients"},
                      color_discrete_sequence=(['darkblue']))
    #Ethnicity data and graph
    df_eth =df['EthnicityDSC'].value_counts().to_frame(name = 'Number of patients')
    pat_eth_bar = px.bar(df_eth.head(10), y = 'Number of patients', title = 'Ethnical Distribution of Patients: Top 10', labels = {"index" : "Ethnicity", "Patients" : "Number of Patients"},
                     color_discrete_sequence=(['darkturquoise']))
    #Patient's Age
    df_age = df['Pat_age'].value_counts().to_frame(name = "Patient's Age")
    pat_age_bar = px.bar(df_age, y = "Patient's Age", title = 'Age Distribution Amongst Patients', labels = {'index':'Age', "Patient's Age": "Patient's Age"},
                         color_discrete_sequence=(['Blue']))

    #Distribution of procedures
    proc_distr_pie = px.pie(df_prim_rev['procedures.ShortDSC'], names = df_prim_rev['procedures.ShortDSC'], title = "Distribution of Procedures", color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
                                        'lightblue', 'skyblue', 'steelblue', 'mediumblue'))
    
    # Old Distribution of Procedures: ignore 
    #proc_distr_pie = px.pie(df['ShortDSC'], names = df['ShortDSC'], title = "Distribution of Procedures", color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    
                                        #'lightblue', 'skyblue', 'steelblue', 'mediumblue'))
                                
    #Parse only revision data
    df_rev = df[~df['procedures.ShortDSC'].str.contains('Total')]
    proc_revision_pie = px.pie(df_rev['procedures.ShortDSC'], names = df_rev['procedures.ShortDSC'], title = "Distribution of Revision Procedures", color_discrete_sequence=('wheat', 'burlywood', 'tan', 'rosybrown', 'goldenrod', 'peru', 'saddlebrown', 'sienna','maroon'))
    
    
    #Hip related CPT codes and description
    hip_related_CPTs = df['procedures.ShortDSC'].str.contains('Hip')
    df_hip_related_CPTs = df[hip_related_CPTs]    
    df_hip_shortDSC = df_hip_related_CPTs['procedures.ShortDSC'].value_counts().to_frame(name='value_counts')
    hip_distr_bar = px.bar(df_hip_shortDSC, y = 'value_counts', title = 'Distribution of Hip Procedures',
                labels = {"index": "Procedure Type", "value_counts": "Number of Procedures"},  color_discrete_sequence=(['rosybrown']))
    
    #Knee related CPT codes and descriptions
    knee_related_CPTs = df['procedures.ShortDSC'].str.contains('Knee')
    df_knee_related_CPTs = df[knee_related_CPTs]
    df_knee_shortDSC = df_knee_related_CPTs['procedures.ShortDSC'].value_counts().to_frame(name='value_counts')    
    knee_distr_bar = px.bar(df_knee_shortDSC, y = 'value_counts', title = 'Distribution of Knee Procedures',
                            labels = {"index": "Procedure Type", "value_counts": "Number of Procedures"},  color_discrete_sequence=(['plum']))
    
   #Top 10 ICD codes
    ICD_data = {'gensurgcomorb.Acute_MI_ICD10': [sum(df['gensurgcomorb.Acute_MI_ICD10'].value_counts())],

               'gensurgcomorb.CHF_ICD10' : [sum(df['gensurgcomorb.CHF_ICD10'].value_counts())],

               'gensurgcomorb.Peripheral_vascular_disease_ICD10': [sum(df['gensurgcomorb.Peripheral_vascular_disease_ICD10'].value_counts())],

               'gensurgcomorb.CVA_ICD10' : [sum(df['gensurgcomorb.CVA_ICD10'].value_counts())],

               'gensurgcomorb.Dementia_ICD10' :[sum(df['gensurgcomorb.Dementia_ICD10'].value_counts())],

               'gensurgcomorb.Pulmonary_disease_ICD10' :[ sum(df['gensurgcomorb.Pulmonary_disease_ICD10'].value_counts())],

               'gensurgcomorb.Connective_tissue_disorder_ICD10' :[ sum(df['gensurgcomorb.Connective_tissue_disorder_ICD10'].value_counts())],

               'gensurgcomorb.Peptic_ulcer_ICD10' : [sum(df['gensurgcomorb.Peptic_ulcer_ICD10'].value_counts())],

               'gensurgcomorb.Liver_disease_ICD10' : [sum(df['gensurgcomorb.Liver_disease_ICD10'].value_counts())],

               'gensurgcomorb.Diabetes_ICD10' : [sum(df['gensurgcomorb.Diabetes_ICD10'].value_counts())],

               'gensurgcomorb.Diabetes_complications_ICD10' : [sum(df['gensurgcomorb.Diabetes_complications_ICD10'].value_counts())],

               'gensurgcomorb.Paraplegia_ICD10' : [sum(df['gensurgcomorb.Paraplegia_ICD10'].value_counts())],

               'gensurgcomorb.Renal_disease_ICD10':[ sum(df['gensurgcomorb.Renal_disease_ICD10'].value_counts())],

               'gensurgcomorb.Cancer_ICD10' : [sum(df['gensurgcomorb.Cancer_ICD10'].value_counts())],

               'gensurgcomorb.Metastatic_cancer_ICD10' : [sum(df['gensurgcomorb.Metastatic_cancer_ICD10'].value_counts())],

               'gensurgcomorb.Severe_liver_disease_ICD10' : [sum(df['gensurgcomorb.Severe_liver_disease_ICD10'].value_counts())],

               'gensurgcomorb.HIV_ICD10' : [sum(df['gensurgcomorb.HIV_ICD10'].value_counts())],

               'gensurgcomorb.ALL_ICD10' : [sum(df['gensurgcomorb.ALL_ICD10'].value_counts())],

               'gensurgcomorb.Osteoporosis_ICD10' : [sum(df['gensurgcomorb.Osteoporosis_ICD10'].value_counts())],

               'gensurgcomorb.Mental_and_behavioral_disorders_due_to_psychoactive_substance_abuse_ICD10' : [sum(df['gensurgcomorb.Mental_and_behavioral_disorders_due_to_psychoactive_substance_abuse_ICD10'].value_counts())],

               'gensurgcomorb.Schizophrenia_schizotypal_delusional_and_other_nonmood_disorders_ICD10' : [sum(df['gensurgcomorb.Schizophrenia_schizotypal_delusional_and_other_nonmood_disorders_ICD10'].value_counts())],

               'gensurgcomorb.Mood_affective_disorders_ICD10' :[ sum(df['gensurgcomorb.Mood_affective_disorders_ICD10'].value_counts())],

               'gensurgcomorb.Anxiety_dissociative_stressrelated_somatoform_and_other_nonpsychotic_mental_disorders_ICD10' : [sum(df['gensurgcomorb.Anxiety_dissociative_stressrelated_somatoform_and_other_nonpsychotic_mental_disorders_ICD10'].value_counts())],

               'gensurgcomorb.PULMONARY_EMBOLISM_ACUTE_ICD10' : [sum(df['gensurgcomorb.PULMONARY_EMBOLISM_ACUTE_ICD10'].value_counts())],

               'gensurgcomorb.PULMONARY_EMBOLISM_CHRONIC_ICD10' : [sum(df['gensurgcomorb.PULMONARY_EMBOLISM_CHRONIC_ICD10'].value_counts())],

               'gensurgcomorb.ACUTE_DVT_LOWER_EXTREMITY_ICD10' :[ sum(df['gensurgcomorb.ACUTE_DVT_LOWER_EXTREMITY_ICD10'].value_counts())],

               'gensurgcomorb.CHRONIC_DVT_LOWER_EXTREMITY_ICD10' :[ sum(df['gensurgcomorb.CHRONIC_DVT_LOWER_EXTREMITY_ICD10'].value_counts())],

               'gensurgcomorb.ACUTE_DVT_UPPER_EXTREMITY_ICD10' :[ sum(df['gensurgcomorb.ACUTE_DVT_UPPER_EXTREMITY_ICD10'].value_counts())],

               'gensurgcomorb.CHRONIC_DVT_UPPER_EXTREMITY_ICD10' : [sum(df['gensurgcomorb.CHRONIC_DVT_UPPER_EXTREMITY_ICD10'].value_counts())],

               'gensurgcomorb.PHLEBITIS_AND_THROMBOPHLEBITIS_OF_LOWER_EXTREMITY_ICD10' : [sum(df['gensurgcomorb.PHLEBITIS_AND_THROMBOPHLEBITIS_OF_LOWER_EXTREMITY_ICD10'].value_counts())],

               'gensurgcomorb.PHLEBITIS_AND_THROMBOPHLEBITIS_OF_UPPER_BODY_OR_EXTREMITY_ICD10' :[ sum(df['gensurgcomorb.PHLEBITIS_AND_THROMBOPHLEBITIS_OF_UPPER_BODY_OR_EXTREMITY_ICD10'].value_counts())],

               'gensurgcomorb.UNSPECIFIED_PHLEBITIS_AND_THROMBOPHLEBITIS_ICD10' :[ sum(df['gensurgcomorb.UNSPECIFIED_PHLEBITIS_AND_THROMBOPHLEBITIS_ICD10'].value_counts())]}


    df_ICD = pd.DataFrame.from_dict(ICD_data, columns=['Comorbidity'], orient='index')

    #find the top 10 highest numbers
    
    ICD10_bar = px.bar(df_ICD.head(10).sort_values(by = 'Comorbidity',ascending = False), title = 'Top 10 Most Common ICD10 Comorbidities',
    
                       labels={'index': 'Types of Comorbidities', 'value':'Frequency'}, color ='value',  color_continuous_scale = 'ice')
    
    #Parse discharge distribution data
    #TODO: The difference descriptions seem to refer to different discharges so hesitant to lump together into bigger categories 
    df_discharge = df.copy()
    #df_discharge.loc[df_discharge['ShortDSC'].str.contains('REVIS'), 'ShortDSC'] = 'REVISION'
    discharge_distr_pie = px.pie(df_discharge['gensurgcomorb.DischargeDispositionDSC'], names = df_discharge['gensurgcomorb.DischargeDispositionDSC'], title = "Discharge Disposition Distribution",
                     color_discrete_sequence=('powderblue', 'lightsteelblue', 'lightskyblue', 'teal', 'turquoise', 'aquamarine', 'aqua', 'lightcyan'))
    
    ##Financial data - who pays for the patient's care
<<<<<<< HEAD
    financial_pie = px.pie(df['gensurgcomorb.OriginalFinancialClassDSC'], names=df['gensurgcomorb.OriginalFinancialClassDSC'], title = ('Financial data distribution'),  
                           color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
                                                    'skyblue', 'steelblue'))
=======
    #financial_pie = px.pie(df['gensurgcomorb.OriginalFinancialClassDSC'], names=df['gensurgcomorb.OriginalFinancialClassDSC'], title = ('Financial data distribution'),  
    #                       color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    #                                                'skyblue', 'steelblue'))
    financial_pie = 0
>>>>>>> parent of 96c07a8 (Removed df_diag)
    
    
    #Revenue as per location - this is quite irrelevant 
    revenue_location_pie = px.pie(df['gensurgcomorb.RevenueLocationNM'], names = df["gensurgcomorb.RevenueLocationNM"], title = ('Revenue Based on Locations'),
                                  color_discrete_sequence=('wheat', 'burlywood', 'tan', 'rosybrown', 'goldenrod', 'peru', 'saddlebrown', 'sienna',
                                                    'maroon'))
    #Provider data and graph: who are providing for the patient's procedures
    df_provider = df['gensurgcomorb.ProviderSpecialtyDSC'].value_counts().to_frame(name='value_counts')
    provider_specialty_bar = px.bar(df_provider, y = 'value_counts', title = "Provider Specialties Based Distribution", color_discrete_sequence=(['skyblue']))
    
    #Hip diagnoses
    df_hip_diag = df_hip_related_CPTs['gensurgcomorb.ICD_DSC_1'].value_counts().to_frame(name='value_counts')
    hip_diag_bar = px.bar(df_hip_diag.head(10), y = 'value_counts' ,title = 'Hip Diagnoses', color_discrete_sequence=(['darkblue']))
    #hip_diag_pie = px.pie(df_hip_related_CPTs['ICD_DSC_1'], names = df_hip_related_CPTs['ICD_DSC_1'], title = 'Hip Diagnoses', color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
     #                                               'skyblue', 'steelblue'))
    
    #Knee Diagnoses
    df_knee_diag = df_knee_related_CPTs['gensurgcomorb.ICD_DSC_1'].value_counts().to_frame(name='value_counts')
    #knee_diag_pie = px.pie(df_knee_related_CPTs['ICD_DSC_1'], names=df_knee_related_CPTs['ICD_DSC_1'],title = 'Knee Diagnoses', color_discrete_sequence=('cyan', 'darkturquoise', 'lightseagreen', 'teal', 'cadetblue', 'aquamarine', 'mediumaquamarine', 'powderblue',
    #                                               'skyblue', 'steelblue'))
    knee_diag_bar = px.bar(df_knee_diag.head(10), y = 'value_counts' ,title = 'Knee Diagnoses', color_discrete_sequence=(['darkblue']))


    #Patients' BMI data
    df_BMI= df['BMI'].value_counts().to_frame(name = 'Patients')
   # bmi_bar = px.bar(df_BMI, y = 'Patients', title = "BMI Distribution of Patients", labels = {'index': 'BMI', 'Patients': 'Patients'}, 
   #                   color_discrete_sequence=(['#008E97'])) 
    bmi_bar = px.histogram(df['BMI'], x = 'BMI', range_x=[0,100], nbins=100)
    bmi_bar.update_layout(bargap=0.2)
    
    tableBMI = dash_table.DataTable(
                                 df_BMI.to_dict('index'), [{'name':i, 'id': i} for i in df.columns], id='tbl1'
                            )
    #find the distribution of diagnosis - overall categories
    df_diag_count = df_diag['Category'].value_counts().to_frame(name = 'count per category')
    diag_gen_bar = px.bar(df_diag_count, y = 'count per category',title = 'Distribution of General Surgeon Diagnoses', 
                          color_discrete_sequence = (["DarkOliveGreen"]))
    
<<<<<<< HEAD
=======
    """
>>>>>>> parent of 96c07a8 (Removed df_diag)
    df_alc_temp = df['alc_use.AlcoholDrinksPerWeekCNT'].value_counts().to_frame(name = 'Number of Patients')
    alc_use_bar = px.bar(df_alc_temp, y = 'Number of Patients', labels = {'index': 'Number of Drinks'},title = 'Distribution of Patients Alcoholic Drinks Consumption Per Week',
                         color_discrete_sequence=(['#966fd6']))
    
    alc_use_type_pie = px.pie(df['alc_use.HistoryOfDrinkTypesCD'], names=(df['alc_use.HistoryOfDrinkTypesDSC']), title = 'Type of Alcoholic Drink Consumed by Patients',
                              color_discrete_sequence=(['#93ccea', '#e0ffff', '#acace6', '#b768a2']))
    
    
    
    return (proc_distr_pie, proc_revision_pie, hip_distr_bar, knee_distr_bar, ICD10_bar, discharge_distr_pie, financial_pie, revenue_location_pie, provider_specialty_bar,
            pat_race_bar, pat_eth_bar, hip_diag_bar, knee_diag_bar, pat_age_bar, bmi_bar, diag_gen_bar, alc_use_bar, alc_use_type_pie, tableBMI )
