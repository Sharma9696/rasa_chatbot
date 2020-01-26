# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 13:20:58 2019

@author: kamalpreet.singh
"""

import json

with open("23-Jan-2020.json") as json_file:
    print(json_file)
    data = json.load(json_file)

ls =[]
for i in data:
    try:
        ls.append(i['user_text'])
    except:
        pass

for i in ls:
    if i in ['getting user info from api','break out of current story']:
        pass
    else:
        print(i)



df = []
for i in data:
    for j,k in i.items():
        if j == "events":
            for l in k:
                for m,n in l.items():
                    if m == "parse_data":
                        x = {'text': n['text'],
                             'intent': n['intent']['name'],
                             'confidence': n['intent']['confidence'],
                             'entities': n['entities']}
                        df.append(x)
                        



"""from D directory final logs"""
import os
import json
import xlsxwriter

basepath = "Live_chat_logs"

ls=[]
for folders in os.listdir(basepath):
    for file in os.listdir(os.path.join(basepath,folders)):
        if os.path.isfile(os.path.join(basepath,folders,file)):
            with open(basepath+'/'+folders+'/'+file,'r') as json_file:
                try:
                    data = json.load(json_file)
                    for i in data:
                        try:
                            ls.append(i['user_text'])
                        except:
                            pass
                except:
                    pass


workbook = xlsxwriter.Workbook(basepath+"/user_inputs.xlsx")
worksheet = workbook.add_worksheet()
row = 0
column = 0
for i in ls:
    if i in ['getting user info from api','break out of current story']:
        pass
    else:
        worksheet.write(row, column, i)
        row += 1
workbook.close()

                
                
                
                
                
        
    
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
