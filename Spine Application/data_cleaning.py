# -*- coding: utf-8 -*-
"""
Data cleaning file

Created on Mon Aug 22 11:25:37 2022

@author: kbdet
"""

import os
import pandas as pd
import numpy as np
import csv

# Set directory
#TODO: not sure why I had to do this - will need to change for every person running this code
mydir = r'C:/Users/kbdet/Documents/fixus-app'

# Add paths
PATHS = {
    'data_aaos' : os.path.join(mydir,'data','aaos_database'),
    'trial_data' : os.path.join(mydir,'data','trial_data')
    }
    
# Read in CSV files
#df = pd.read_excel(os.path.join(PATHS['data_aaos'], 'data2021cleanedcurrent.xlsx'), dtype={'ID':str})
#df_mgh = df.copy()

df = pd.read_excel(os.path.join(PATHS['data_aaos'], 'data2021cleanedcurrent.xlsx'), dtype={'ID':str})



#%%

#Remove TREAT THIGH FRACTURE, INSERT/REMOVE DRUG IMPLANT DEVICE, CPTR-ASST DIR MS PX, and TREAT HIP DISLOCATION
# from the dataset
searchfor = ['TREAT', 'DRUG IMPLANT DEVICE', 'CPTR']
df_clean = df_mgh[~df_mgh['procedures.ShortDSC'].str.contains('|'.join(searchfor))]

#remove patient duplicates (based on comorbidities) 
#some patients coded for two separate procedures (e.g. total hip replacements and revise hip replacement)
df_mgh_clean = df_clean.drop_duplicates(subset = ['PatientID', 'procedures.ShortDSC','surgeons.CaseID'],
                                      keep = 'first').reset_index(drop = True)


#take out comorbidities.ProblemStatusDSC = Active

# Set variables
time_period = '2021Q3'


#%% Export CSV with surgeon usernames and passwords

#TODO: This needs to be across quarters - figure out how to make this better
list_surgeons = pd.Series(df_mgh['surgeons.PrimarySurgeon']).unique().tolist()
#print(list_surgeons)
#create username for each primary surgeon using a loop
USER_TO_NAME = {}
user_list= {}

for x in list_surgeons:
    un = []
    if type(x) == str:
        for i in range(len(list_surgeons)): 
            un = x[0] + x.rsplit(' ', 1)[1]
            USER_TO_NAME.update({str(un) : x})
            user_list.update({str(un): (x[0: 2] + x[0:2])})
            
df_users = pd.DataFrame(user_list,index=[0])

#Save as a csv file in app_data folder
filepath = os.path.join(mydir,'data','app_data','user_list.csv')
df_users.to_csv(filepath,index=False)


#%% Export CSV with data for all MGB
#TODO: Create file with all MGB data and export

out = df_mgh_clean.copy()

out = out[out.duplicated('PatientID',keep=False)]


#%%
#Patient info at a glance data




AJRRPat_total = len(list(df_mgh_clean['PatientID'].unique())) # int of total patients on the spreadsheet

males_patients = list(df_mgh_clean['SexDSC'] == 'Male')

#find the indicies of the males in the data column

males = list(filter(lambda i: males_patients[i], range(len(males_patients))))

males_ratio = round((len(males) / (AJRRPat_total) *100)) #% of men on the spreadsheet

female_ratio = (100 - males_ratio)

if round((703 * (df_mgh_clean['weight.WeightOz']*0.0625) / (df_mgh_clean['height.HeightIn'])**2).mean()) < 100:
    BMI_total = round((703 * (df_mgh_clean['weight.WeightOz']*0.0625) / (df_mgh_clean['height.HeightIn'])**2).mean())
else:
    BMI_total= 'not available'

#avergae length of stay, aka the average of the column named Lenght of Stay

avg_length_of_stay = round(df_mgh_clean["surgeons.Length of Stay"].mean())

avg_pat_age = round(df_mgh_clean['Pat_age'].mean())


pat_info_data = {'Year_quarter': time_period, 
                 'Total_patients': AJRRPat_total,
                 'Male_ratio' : males_ratio,
                 'Female_ratio' : female_ratio,
                 'Avg_length_of_stay' : avg_length_of_stay,
                 'BMI_total' : BMI_total,
                 'Avg_pat_age' : avg_pat_age}

pat_info = pd.DataFrame(pat_info_data, index=[0])

#Save as a csv file in app_data folder
filepath = os.path.join(mydir,'data','app_data','patient_info.csv')
pat_info.to_csv(filepath,index=False)


#TODO: check to make sure when cutting duplicates that we are not cutting off two different procedures for the same patient

#%%
#TODO: Separate data into surgeon speific CSV failes



#%%
#TODO: Export CSV files compressed with only graphing data





