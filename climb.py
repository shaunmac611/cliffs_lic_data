# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 11:25:01 2021

@author: Shaun
"""
import datetime as dt
import pandas as pd
import re

YDS_DICT={'N/A':'N/A','3-4':0,'5':1,'5.0':1,'5.1':2,'5.2':3,'5.3':4,'5.4':5,
          '5.5':6,'5.6':7,'5.7':8,'5.8':9,'5.9':10,
          '5.10a':11,'5.10b':12,'5.10c':13,'5.10d':14,
          '5.11a':15,'5.11b':16,'5.11c':17,'5.11d':18,
          '5.12a':19,'5.12b':20,'5.12c':21,'5.12d':22,
          '5.13a':23,'5.13b':24,'5.13c':25,'5.13d':26,
          '5.14a':27,'5.14b':28,'5.14c':29,'5.14d':30,
          '5.15a':31,'5.15b':32,'5.15c':33,'5.15d':34}

BOULDER_DICT={'N/A':'N/A','VB':12,'V0':13,'V1':14,'V2':15,'V3':16,'V4':17,'V5':18,
              'V6':19,'V7':20,'V8':21,'V9':22,'V10':23,'V11':24,'V12':25,
              'V13':26,'V14':27,'V15':28,'V16':29,'V17':30}

class Climb:
    def __init__(self, climb_soup, climb_type=None):
        self.soup = climb_soup
        if climb_type:
            self.climb_type = climb_type

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
             'type':[self.climb_type],
             'grade':[self.grade],
             'rating':[self.rating],
             'first_ascent':[self.first_ascent],
             'total_ascents':[self.total_ascents],
             'location':[self.location],
             'num_grade':[self.numerical_grade]}
        return pd.DataFrame(d)
    
    def to_string(self):
        return self.name + ' || Grade: ' + self.grade + ' || FA: ' + str(self.first_ascent)

class MP_Climb(Climb):
    
    def __init__(self, climb_soup, climb_type=None):
        super().__init__(climb_soup, climb_type)
        route_desc = self.soup.find_all(class_="description-details")[0].get_text().replace('\n',"")
        route_desc = re.sub('\s+',' ',route_desc)
        
        self.climb_type = route_desc.split('Type: ')[1].split(' FA:')[0]
        self.grade = self.soup.find_all(class_="rateYDS")[0].get_text()[:-4]
        self.rating = float(self.soup.find(id="route-star-avg").get_text().split('Avg: ')[1].split(' from')[0])
        self.name = self.soup.find("meta", {"property":"og:title"})['content']
        self.ascents_link = [i for i in self.soup.find_all('a') if '/route/' in str(i)][0].get('href')
        self.total_ascents = len(self.ascents_link)
        self.first_ascent = route_desc.split('FA:')[1].split(' Page Views:')[0]
        self.unique_id = 'MP_'#Need to add route id here
        self.numerical_grade = self.get_numerical_grade(self.grade)
        self.location = self.get_location()
    
    def get_location(self):
        location_info = self.soup.find_all(class_="mb-half small text-warm")[0]
        locations = [i.get_text() for i in location_info.find_all('a')][1:]
        return ' || '.join(locations)
    
class VL_Climb(Climb):
    
    def __init__(self, climb_soup, climb_type=None):
        super().__init__(climb_soup, climb_type)
        self.grade = self.soup.find("meta", {"property":"vertical-life:rt_difficulty"})['content']
        self.rating = self.get_avg_rating()
        self.name = self.get_color() + ' ' + self.grade
        self.total_ascents, self.first_ascent = self.get_ascent_info()
        self.unique_id = 'VL_'+self.soup.find("meta", {"property":"al:ios:url"})['content'].split('/')[-1]
        self.numerical_grade = self.get_numerical_grade(self.grade)
        self.location = 'The Cliffs LIC' #Temporary
        
    def get_avg_rating(self):
        stars = self.soup.find_all(class_="stat average-rating")
        stars = str(stars).split('class="star" src="')
        avg_stars=0
        for star in stars:
            if 'inverted' in star.split('">')[0]:
                avg_stars = avg_stars+1
        return avg_stars
    
    def get_ascent_info(self):
        ascent_dates = self.soup.find_all(class_="hidden-xs date")
        total_ascents = len(ascent_dates)
        first_ascent = str(ascent_dates[-1]).split('>')[1].split('<')[0]
        first_ascent = dt.datetime.strptime(first_ascent, '%d.%m.%Y')
        return total_ascents, first_ascent
    
    def get_color(self):
        possible_colors = ['Lime Green','Purple','Yellow','Pink','Grey','Blue','White',
                           'Tan','Red','Black']
        color = self.soup.find("meta", {"property":"og:title"})['content']
        color = color.split('(')[0].strip()
        color_list = [i for i in possible_colors if i in color]
        if not color_list:
            return color
        else:
            return color_list[0]
