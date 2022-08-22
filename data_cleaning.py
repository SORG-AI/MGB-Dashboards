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


# Add paths
PATHS = {
    'images': os.path.join('images'),
    'data_aaos' : os.path.join('data','aaos_database'),
    'trial_data' : os.path.join('data','trial_data')
    }
    
# Read in CSV files
df = pd.read_excel(os.path.join(PATHS['data_aaos'], 'data2021cleanedcurrent.xlsx'), dtype={'ID':str})

df_mgh = df.copy()


#%%
#TODO: Pull out all surgeon names

list_surgeons = pd.Series(df['surgeons.PrimarySurgeon']).unique().tolist()
#print(list_surgeons)
#create username for each primary surgeon using a loop
USER_TO_NAME = {}
user_list= {}

user_info = ['username','password']

for x in list_surgeons:
    un = []
    if type(x) == str:
        for i in range(len(list_surgeons)): 
            un = x[0] + x.rsplit(' ', 1)[1]
            USER_TO_NAME.update({str(un) : x})
            user_list.update({str(un): (x[0: 2] + x[0:2])})
            
print(user_list)



#%%

df_users = pd.DataFrame(user_list,index=[0])

#%%
#TODO: Create file with all MGB data and export


#%%
#TODO: Separate data into surgeon speific CSV failes



#%%
#TODO: Export CSV files compressed with only graphing data

with open('test.csv','w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = user_info)
    #writer.writeheader()
    writer.writerows(USER_LIST)



