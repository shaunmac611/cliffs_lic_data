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

BOULDER_DICT={"N/A":"N/A",'VB':12,'V0':13,'V1':14,'V2':15,'V3':16,'V4':17,'V5':18,
              'V6':19,'V7':20,'V8':21,'V9':22,'V10':23,'V11':24,'V12':25,
              'V13':26,'V14':27,'V15':28,'V16':29,'V17':30}

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

class Climber:

    def __init__(self, climber_soup, gym=None):
        self.soup = climber_soup
        self.name = self.soup.find("title").get_text()[:-1*len(' vertical-life profile')]
        self.app_id = self.soup.find("meta", {"property":"al:ios:url"})['content'].split('/')[-1]
        self.init_core_info()
        self.sends = self.get_sends()
        self.get_top_data(top=10)
    
    def init_core_info(self):
        class_values = [div_class.get_text() for div_class in self.soup.find_all("div", {"class": "value"})][2:]
        class_names = [div_class.get_text() for div_class in self.soup.find_all("div", {"class": "name"})]
        climber_info = {class_names[i]: class_values[i] for i in range(len(class_names))}
        all_class_names = CLASS_NAMES_DEFAULT
        for i in list(climber_info.keys()):
            all_class_names[i] = climber_info[i]
        
        self.zlags = int(all_class_names['zlags'].replace(" ",""))
        self.meters_climbed = int(all_class_names['meters climbed'].replace(" ",""))
        self.total_points = int(all_class_names['total points'].replace(" ",""))
    
    def to_df(self):
        d = {'app_id':[self.app_id],
             'name':[self.name],
             'zlags':[self.zlags],
             'meters_climbed':[self.meters_climbed],
             'total_points':[self.total_points],
             'best_lead_grade':[self.best_lead_grade],
             'best_boulder_grade':[self.best_boulder_grade],
             'top_ten_avg_lead_grade':[self.top_ten_avg_lead_grade],
             'top_ten_avg_boulder_grade':[self.top_ten_avg_boulder_grade],
             }
        return pd.DataFrame(d)
    
    def get_sends(self):
        climbs = self.soup.find_all(class_="route")
        columns = ['color', 'grade', 'difficulty', 'route_type', 'location']
        route_data = pd.DataFrame(columns = columns)
        lic_climbs = [climb for climb in climbs if 'The Cliffs at LIC' in climb.get_text()]
        for climb in lic_climbs:
            items = str(climb).split('\n')
            grade=items[2].split(" ")[-1]
            color=items[2].split(" ")[-2]
            location=items[5].split(">")[1].split('<')[0]
            if '5.' in climb.get_text() or '3-4' in climb.get_text():
                route_type = 'roped'
                difficulty = YDS_DICT[grade]
            else:
                route_type = 'boulder'
                difficulty = BOULDER_DICT[grade]
            route_data = append_dataframes(route_data, pd.DataFrame([[color,grade,difficulty,route_type,location]], columns=columns))
        return route_data

    def get_top_data(self, top=10):
        top_routes = self.sends.loc[self.sends['route_type']=='roped'].sort_values(by='difficulty', axis=0, ascending=False)[:top].reset_index()
        top_boulders = self.sends.loc[self.sends['route_type']=='boulder'].sort_values(by='difficulty', axis=0, ascending=False)[:top].reset_index()
        
        if not top_routes.empty:
            self.best_lead_grade = top_routes['grade'].iloc[0]
            self.top_ten_avg_lead_grade = list(YDS_DICT.keys())[list(YDS_DICT.values()).index(round(top_routes['difficulty'].mean()))]
        else:
            self.best_lead_grade = "N/A"
            self.top_ten_avg_lead_grade = "N/A"
        if not top_boulders.empty:
            self.best_boulder_grade = top_boulders['grade'].iloc[0]
            self.top_ten_avg_boulder_grade = list(BOULDER_DICT.keys())[list(BOULDER_DICT.values()).index(round(top_boulders['difficulty'].mean()))]
        else:
            self.best_boulder_grade = "N/A"
            self.top_ten_avg_boulder_grade = "N/A"

    def to_string(self):
        return self.name + ': Climbs:' + self.top_ten_avg_lead_grade + "/" + self.top_ten_avg_boulder_grade\
               + ". Has sent " + self.best_lead_grade + "/" + self.best_boulder_grade

def append_dataframes(big_df, small_df):
    if big_df.empty:
        big_df = small_df.copy()
    else:
        big_df = big_df.append(small_df)
    return big_df