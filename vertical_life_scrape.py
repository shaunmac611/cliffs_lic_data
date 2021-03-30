# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 19:00:44 2021

@author: Shaun
"""
import pandas as pd
import os
import urllib
from urllib.error import HTTPError
from bs4 import BeautifulSoup

from climb import Climb

VL_SITE = "https://www.vertical-life.info/"
GYM_SITE = "en/indoor/the-cliffs-at-lic/"
DATA_FILE = 'cliffs_climbs.xlsx'

def cliffs_climb_scrape():
    webUrl = urllib.request.urlopen(VL_SITE+GYM_SITE)
    soup = BeautifulSoup(webUrl, 'html.parser')
    
    count=0
    for table in soup.find_all('table'):
        if count==2:
            roped = table.find_all(class_="route")
        elif count==3:
            boulders = table.find_all(class_="route")
        count=count+1
        
    roped_data = loop_through_climbs(roped, 'roped')
    boulder_data = loop_through_climbs(boulders, 'boulder')
    climb_data_df = roped_data.append(boulder_data)
    
    if os.path.isfile(DATA_FILE):
        climb_data_file = pd.read_excel(DATA_FILE, usecols=climb_data_df.columns, dtype={'app_id':str})
        climb_data_file['current_state']=False
        climb_data_file = add_to_dataframe(climb_data_file, climb_data_df)
        unique_cols = ['app_id', 'type', 'grade', 'color', 'image', 'first_ascent','num_grade']
        climb_data_file = climb_data_file.drop_duplicates(subset=unique_cols, keep='last')
        climb_data_file.to_excel(DATA_FILE)
    else:
        climb_data_df.to_excel(DATA_FILE)

def loop_through_climbs(routes, climb_type):
    route_data = pd.DataFrame()
    for route in routes:
        climb_url = is_climb_url(route)
        if climb_url != False:
            climb_soup = BeautifulSoup(climb_url, 'html.parser')
            climb = Climb(climb_soup, climb_type)
            route_data = add_to_dataframe(route_data, climb.to_df())
    return route_data

def is_climb_url(route):
    if 'href=' in str(route):
        climb_url = str(route).split('href=')[1].split('>')[0][1:-1]
        try:
            climb_url = urllib.request.urlopen(VL_SITE+climb_url)
            return climb_url
        except HTTPError:
            return False
    else:
        return False

def add_to_dataframe(big_df, small_df):
    if big_df.empty:
        big_df = small_df.copy()
    else:
        big_df = big_df.append(small_df)
    return big_df
