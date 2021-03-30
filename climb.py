# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 20:41:05 2021

@author: Shaun
"""
import pandas as pd
import datetime as dt

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

COLORS=['Lime Green','Purple','Yellow','Pink','Grey','Blue','White',
        'Tan','Red','Black']

class Climb:

    def __init__(self, climb_soup, climb_type):
        self.climb_type = climb_type
        self.grade = climb_soup.find("meta", {"property":"vertical-life:rt_difficulty"})['content']
        self.image = climb_soup.find("meta", {"property":"og:image"})['content']
        self.rating = self.get_avg_rating(climb_soup)
        self.ascents, self.first_ascent = self.get_ascent_info(climb_soup)
        self.numerical_grade = self.get_numerical_grade(self.grade, self.climb_type)
        self.color = self.get_color(climb_soup)
        self.app_id = climb_soup.find("meta", {"property":"al:ios:url"})['content'].split('/')[-1]
        self.current_state = True
        self.date_updated = dt.date.today()

    def get_avg_rating(self, climb_soup):
        stars = climb_soup.find_all(class_="stat average-rating")
        stars = str(stars).split('class="star" src="')
        avg_stars=0
        for star in stars:
            if 'inverted' in star.split('">')[0]:
                avg_stars = avg_stars+1
        return avg_stars
    
    def get_ascent_info(self, climb_soup):
        ascent_dates = climb_soup.find_all(class_="hidden-xs date")
        ascents = len(ascent_dates)
        first_ascent = str(ascent_dates[-1]).split('>')[1].split('<')[0]
        first_ascent = dt.datetime.strptime(first_ascent, '%d.%m.%Y')
        return ascents, first_ascent
    
    def get_numerical_grade(self, grade, climb_type):
        if grade in YDS_DICT:
            num_grade = YDS_DICT[grade]
        elif grade in BOULDER_DICT:
            num_grade = BOULDER_DICT[grade]
        else:
            num_grade = 0
        return num_grade
    
    def get_color(self, climb_soup):
        color = climb_soup.find("meta", {"property":"og:title"})['content']
        color = color.split('(')[0].strip()
        color_list = [i for i in COLORS if i in color]
        if not color_list:
            return color
        else:
            return color_list[0]
    
    def to_df(self):
        d = {'app_id':[self.app_id],
             'type':[self.climb_type],
             'grade':[self.grade],
             'color':[self.color],
             'image':[self.image],
             'rating':[self.rating],
             'first_ascent':[self.first_ascent],
             'total_ascents':[self.ascents],
             'num_grade':[self.numerical_grade],
             'date_updated':[self.date_updated],
             'current_state':[self.current_state]}
        return pd.DataFrame(d)
    
    def to_string(self):
        return self.color + ' ' + self.grade + ', first sent on ' + str(self.first_ascent)
