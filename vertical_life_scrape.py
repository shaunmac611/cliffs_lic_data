# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 19:00:44 2021

@author: Shaun
"""
import pandas as pd
import os
import urllib.request as url_request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

from climb import Climb
from climber import Climber

VL_SITE = "https://www.vertical-life.info/"
GYM_SITE = "en/indoor/the-cliffs-at-lic/"

def full_cliffs_scrape():
    _ = cliffs_climb_scrape()
    _ = cliffs_climber_scrape()
    
def cliffs_climber_scrape():
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,} 

    request = url_request.Request(VL_SITE+GYM_SITE,None,headers)
    webUrl = url_request.urlopen(request)
    soup = BeautifulSoup(webUrl, 'html.parser')
    
    climber_data = loop_through_climbers(soup, headers)
    return climber_data

def loop_through_climbers(soup, headers, constant_export = True, suppress_print=False):
    climber_data = pd.DataFrame()
    count=0
    for link in soup.find_all('a'):
        if ('/en/climbers/' in link.get('href')) and (not '\n\n\n\n\n' in link.get_text()):
            count=count+1
            if count>20:
                climber_url = VL_SITE[:-1] + link.get('href')
                if climber_url != False:
                    try:
                        climber_request = url_request.Request(climber_url,None,headers)
                        climber_webUrl = url_request.urlopen(climber_request)
                        climber_soup = BeautifulSoup(climber_webUrl, 'html.parser')
                        try:
                            climber_o = Climber(climber_soup)
                            climber_data = append_dataframes(climber_data, climber_o.to_df())
                            if constant_export:
                                climber_data.to_excel('cliffs_climbers.xlsx', index=False)
                            if count%100==0 and not suppress_print:
                                print('Climber Count: ' + str(count))
                        except TypeError:
                            print('None Type: ' + str(count))
                            continue
                    except URLError:
                        print('URL Error: ' + str(count))
                        continue
    return climber_data


def cliffs_climb_scrape():
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,} 

    request = url_request.Request(VL_SITE+GYM_SITE,None,headers)
    webUrl = url_request.urlopen(request)
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
    export_climb_data(climb_data_df)
    return climb_data_df

def export_climb_data(climb_data_df):
    if os.path.isfile('cliffs_climbs.xlsx'):
        climb_data_file = pd.read_excel('cliffs_climbs.xlsx', usecols=climb_data_df.columns, dtype={'app_id':str})
        climb_data_file['current_state']=False
        climb_data_file = append_dataframes(climb_data_file, climb_data_df)
        unique_cols = ['app_id', 'type', 'grade', 'color', 'image', 'first_ascent','num_grade']
        climb_data_file = climb_data_file.drop_duplicates(subset=unique_cols, keep='last')
        climb_data_file.to_excel('cliffs_climbs.xlsx', index=False)
    else:
        climb_data_df.to_excel('cliffs_climbs.xlsx')

def loop_through_climbs(routes, climb_type):
    route_data = pd.DataFrame()
    for route in routes:
        climb_soup = is_climb_url(route)
        if climb_soup != False:
            #climb_soup = BeautifulSoup(climb_url, 'html.parser')
            climb = Climb(climb_soup, climb_type)
            route_data = append_dataframes(route_data, climb.to_df())
    return route_data

def is_climb_url(route):
    if 'href=' in str(route):
        climb_url = str(route).split('href=')[1].split('>')[0][1:-1]
        try:
            user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            headers={'User-Agent':user_agent,} 
            request = url_request.Request(VL_SITE+climb_url,None,headers)
            webUrl = url_request.urlopen(request)
            climb_soup = BeautifulSoup(webUrl, 'html.parser')
            return climb_soup
        except HTTPError:
            return False
    else:
        return False

def append_dataframes(big_df, small_df):
    if big_df.empty:
        big_df = small_df.copy()
    else:
        big_df = big_df.append(small_df)
    return big_df
