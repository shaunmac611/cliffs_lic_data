# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 20:41:05 2021

@author: Shaun
"""
import pandas as pd

"""Dictionaries used to convert climbing grades to an integer representation
of difficulty"""

YDS_DICT={"N/A":"N/A",'3-4':0,'5':1,'5.0':1,'5.1':2,'5.2':3,'5.3':4,'5.4':5,
          '5.5':6,'5.6':7,'5.7':8,'5.8':9,'5.9':10,
          '5.10a':11,'5.10b':12,'5.10c':13,'5.10d':14,
          '5.11a':15,'5.11b':16,'5.11c':17,'5.11d':18,
          '5.12a':19,'5.12b':20,'5.12c':21,'5.12d':22,
          '5.13a':23,'5.13b':24,'5.13c':25,'5.13d':26,
          '5.14a':27,'5.14b':28,'5.14c':29,'5.14d':30,
          '5.15a':31,'5.15b':32,'5.15c':33,'5.15d':34}

BOULDER_DICT={"N/A":"N/A",'V-easy':11,'VB':12,'V0':13,'V1':14,'V2':15,'V3':16,'V4':17,'V5':18,
              'V6':19,'V7':20,'V8':21,'V9':22,'V10':23,'V11':24,'V12':25,
              'V13':26,'V14':27,'V15':28,'V16':29,'V17':30}

FULL_DICT = BOULDER_DICT
FULL_DICT.update(YDS_DICT)

FRENCH_2_YDS={"N/A":"N/A","1":"5.0","2":"5.1","3":"5.2","3+":"5.3","4":"5.4","4a":"5.4","4b":"5.5",
              "4c":"5.6","5a":"5.7","5b":"5.8","5c":"5.9",
              "6a":"5.10a","6a+":"5.10b","6b":"5.10c","6b+":"5.10d",
              "6c":"5.11a","6c+":"5.11c","7a":"5.11d",
              "7a+":"5.12a","7b":"5.12b","7b+":"5.12c","7c":"5.12d",
              "7c+":"5.13a","8a":"5.13b","8a+":"5.13c","8b":"5.13d",
              "8b+":"5.14a","8c":"5.14b","8c+":"5.14c","9a":"5.14d",
              "9a+":"5.15a","9b":"5.15b","9b+":"5.15c","9c":"5.15d"}

FRENCH_2_HUECO={"N/A":"N/A","3":"V0-","4-":"V0","4":"V0","4+":"V1","5-":"V1",
                "5":"V1","5+":"V2","6A":"V3","6A+":"V3","6B":"V4","6B+":"V4",
                "6C":"V5","6C+":"V5","7A":"V6","7A+":"V7","7B":"V8",
                "7B+":"V8","7C":"V9","7C+":"V10","8A":"V11","8A+":"V12",
                "8B":"V13","8B+":"V14","8C":"V15","8C+":"V16","9A":"V17"}

"""Color options at the cliffs"""
COLORS=['Lime Green','Purple','Yellow','Pink','Grey','Blue','White',
        'Tan','Red','Black']

"""Default option for each climber info, not all are required"""
CLASS_NAMES_DEFAULT = {'zlags':0, 'meters climbed':0, 'total points':0,
                    'best lead grade':'N/A', 'best boulder grade':'N/A'}

class MP_Climber:

    def __init__(self, climber_soup, name='', location=None):
        self.soup = climber_soup
        self.name = name

        self.sends = self.get_sends()
        if location:
            self.sends = self.sends[self.sends['Location'].str.contains(location)]
        self.clean_sends = self.sends
        self.clean_sends = self.clean_sends[~self.clean_sends['Lead Style'].str.contains('Fell')]
        self.clean_sends = self.clean_sends[~self.clean_sends['Lead Style'].str.contains('Hung')]
        
        self.best_boulder, self.avg_boulder = self.get_top_data('Boulder', top=10)
        self.best_sport, self.avg_sport = self.get_top_data(['TR','Trad','Sport'], top=10)
        
    def get_sends(self):
        columns=['Date','Route','Rating','Notes','URL','Pitches','Location',"Avg Stars",
                 "Your Stars","Style","Lead Style","Route Type","Your Rating","Length"]
        send_data = pd.DataFrame(columns = columns)
        count=0
        for line in str(self.soup).split('\n'):
            if line!='':
                current_line = split_exclude_char(line, split_chars=[','], exclude_chars=['"','"'])
                if len(current_line)==14:
                    if count>0:
                        temp_send_data = pd.DataFrame([current_line], columns=columns)
                        send_data = send_data.append(temp_send_data)
            count=count+1
            
        send_data['difficulty'] = send_data['Rating'].map(FULL_DICT)
        for i in range(5,1,-1):
            null_map = send_data['difficulty'].isnull()
            if len(null_map)==0:
                break
            else:
                send_data.loc[null_map, 'difficulty'] = send_data.loc[null_map,'Rating'].str[:i].map(FULL_DICT)
        if send_data['difficulty'].isnull().any():
            send_data = send_data[~send_data['difficulty'].isnull()]
        return send_data

    def to_df(self):
        d = {'name':[self.name],
             'best_lead_grade':[self.best_sport],
             'best_boulder_grade':[self.best_boulder],
             'top_ten_avg_lead_grade':[self.avg_sport],
             'top_ten_avg_boulder_grade':[self.avg_boulder],
             }
        return pd.DataFrame(d)

    def get_top_data(self, route_type, top=10, clean=False):
        if isinstance(route_type,str):
            route_type = [route_type]
        if clean:
            is_sends = self.clean_sends
        else:
            is_sends = self.sends
        top_routes = is_sends.loc[is_sends['Route Type'].str.contains('|'.join(route_type))].sort_values(by='difficulty', axis=0, ascending=False)[:top].reset_index()
        
        if route_type=='Boulder':
            temp_dict = BOULDER_DICT
        else:
            temp_dict = YDS_DICT
            
        if not top_routes.empty:
            best_grade = top_routes['Rating'].iloc[0]
            top_avg_grade = list(temp_dict.keys())[list(temp_dict.values()).index(round(top_routes['difficulty'].mean()))]
        else:
            best_grade = "N/A"
            top_avg_grade = "N/A"
        return best_grade, top_avg_grade

    def to_string(self):
        return self.name + ': Climbs:' + self.top_ten_avg_lead_grade + "/" + self.top_ten_avg_boulder_grade\
               + ". Has sent " + self.best_lead_grade + "/" + self.best_boulder_grade

def append_dataframes(big_df, small_df):
    if big_df.empty:
        big_df = small_df.copy()
    else:
        big_df = big_df.append(small_df)
    return big_df

def split_exclude_char(text, split_chars, exclude_chars):
    if isinstance(split_chars, str):
        split_chars = [split_chars]
    if isinstance(exclude_chars, str):
        exclude_chars = [exclude_chars]

    split=1
    current_line=''
    split_list=[]
    for char in text:
        if char in exclude_chars:
            split=split*-1
        elif char in split_chars and split==1:
            split_list = split_list + [current_line]
            current_line=''
        else:
            current_line = current_line + char
    return split_list
    