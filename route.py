# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 20:41:05 2021

@author: Shaun
"""
import pandas as pd
import re 

"""Dictionaries used to convert climbing grades to an integer representation
of difficulty"""
YDS_DICT={'5':1,'5.1':2,'5.2':3,'5.3':4,'5.4':5,
          '5.5':6,'5.6':7,'5.7':8,'5.8':9,'5.9':10,
          '5.10a':11,'5.10b':12,'5.10c':13,'5.10d':14,
          '5.11a':15,'5.11b':16,'5.11c':17,'5.11d':18,
          '5.12a':19,'5.12b':20,'5.12c':21,'5.12d':22,
          '5.13a':23,'5.13b':24,'5.13c':25,'5.13d':26,
          '5.14a':27,'5.14b':28,'5.14c':29,'5.14d':30,
          '5.15a':31,'5.15b':32,'5.15c':33,'5.15d':34}
BOULDER_DICT={'VB':12,'V0':13,'V1':14,'V2':15,'V3':16,'V4':17,'V5':18,
              'V6':19,'V7':20,'V8':21,'V9':22,'V10':23,'V11':24,'V12':25,
              'V13':26,'V14':27,'V15':28,'V16':29,'V17':30}

"""Color options at the cliffs"""
COLORS=['Lime Green','Purple','Yellow','Pink','Grey','Blue','White',
        'Tan','Red','Black']

class Route:
    def __init__(self, climb_soup):
        self.name = climb_soup.find("meta", {"property":"og:title"})['content']
        self.grade = climb_soup.find_all(class_="rateYDS")[0].get_text()[:-4]
        self.rating = float(climb_soup.find(id="route-star-avg").get_text().split('Avg: ')[1].split(' from')[0])
        self.ascents_link = [i for i in climb_soup.find_all('a') if '/route/' in str(i)][0].get('href')
        
        route_desc = climb_soup.find_all(class_="description-details")[0].get_text().replace('\n',"")
        route_desc = re.sub('\s+',' ',route_desc)
        self.type = route_desc.split('Type: ')[1].split(' FA:')[0]
        self.first_ascent = route_desc.split('FA:')[1].split(' Page Views:')[0]
        self.numerical_grade = self.get_numerical_grade(self.grade)
        
    def get_numerical_grade(self, grade):
        if grade in YDS_DICT:
            num_grade = YDS_DICT[grade]
        elif grade in BOULDER_DICT:
            num_grade = BOULDER_DICT[grade]
        else:
            num_grade = 0
        return num_grade
    
    def to_df(self):
        d = {'name':[self.name],
             'type':[self.type],
             'grade':[self.grade],
             'rating':[self.rating],
             'first_ascent':[self.first_ascent],
             'num_grade':[self.numerical_grade]}
        return pd.DataFrame(d)
    
    def to_string(self):
        return self.name + ' || Grade: ' + self.grade + ' || FA: ' + str(self.first_ascent)
    
