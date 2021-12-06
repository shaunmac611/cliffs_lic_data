# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 17:41:26 2021

@author: Shaun
"""

import pandas as pd
import urllib.request as url_request
from urllib.error import HTTPError
from bs4 import BeautifulSoup

from route import Route
from mp_climber import MP_Climber

FULL_URL = "https://www.mountainproject.com/route-finder?diffMaxaid=75260&diffMaxboulder=20050&diffMaxice=38500&diffMaxmixed=60000&diffMaxrock=12400&diffMinaid=70000&diffMinboulder=20000&diffMinice=30000&diffMinmixed=50000&diffMinrock=1000&is_top_rope=1&is_trad_climb=1&pitches=0&selectedIds=105798167&sort1=area&sort2=rating&stars=0&type=rock&viewAll=1"

def cliffs_climber_scrape():
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,} 

    request = url_request.Request(FULL_URL,None,headers)
    webUrl = url_request.urlopen(request)
    soup = BeautifulSoup(webUrl, 'html.parser')
    constant_export = True
    suppress_print=False
    
    location = 'Gunks'
    climber_data = loop_through_climbs(soup, headers, location, constant_export, suppress_print)
    return climber_data

#output a list of possible grades for ref (maybe have a conversion column)
#output a list of possible send styles to check no other version of TR
#add a uid to ensure no doops
#iterate through crags within an area (All > State > Area> Crag > Route > Ticks/Climbers)
#    'Area' can be multiple steps deep, Area to sub Area to wall to feature is common)




def loop_through_climbs(soup, headers, location, constant_export = True, suppress_print=False):
    climb_data = pd.DataFrame()
    climber_data = pd.DataFrame()
    link_list = []
    count=0
    for link in soup.find_all('a'):
        if not(link.get('href') is None) and ('/route/' in link.get('href')):
            count=count+1
            climb_soup = is_climb_url(link)
            if climb_soup:
                route = Route(climb_soup)
                climber_data, link_list = get_ascent_data(route, climber_data, link_list, location, constant_export=constant_export, suppress_print=suppress_print)
                climb_data = append_dataframes(climb_data, route.to_df())
                if constant_export:
                    climb_data.to_excel(location+'_climbs.xlsx', index=False)
                if count>0 and count%50==0 and not suppress_print:
                    print('=====Climb Count: ' + str(count))
    return climb_data

def get_ascent_data(route, climber_data, link_list, location, constant_export, suppress_print):
    climber_count=0
    soup = is_climb_url(route.ascents_link)
    tick_options = soup.find_all(class_="table table-striped")
    if len(tick_options)>=4:
        ticks = tick_options[3]
        climber_links = ticks.find_all('a')
        for link in climber_links:
            if not (link in link_list):
                link_list = link_list + [link]
                climber_soup = is_climb_url(link.get('href')+'/tick-export')
                climber_o = MP_Climber(climber_soup, link.get_text(), location)
                climber_data = append_dataframes(climber_data, climber_o.to_df())
                climber_count=climber_count+1
                if constant_export:
                    climber_data.to_excel(location+'_climbers.xlsx', index=False)
                if climber_count> 0 and climber_count%250==0 and not suppress_print:
                    print('Climber Count: ' + str(climber_count) + ', ', end=' ')
    return climber_data, link_list

def is_climb_url(link):
    if 'href=' in str(link):
        climb_url = str(link).split('href=')[1].split('>')[0][1:-1]
    else:
        climb_url = link
    try:
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 
        request = url_request.Request(climb_url,None,headers)
        webUrl = url_request.urlopen(request)
        climb_soup = BeautifulSoup(webUrl, 'html.parser')
        return climb_soup
    except HTTPError:
        return False

def append_dataframes(big_df, small_df):
    if big_df.empty:
        big_df = small_df.copy()
    else:
        big_df = big_df.append(small_df)
    return big_df


# =============================================================================
# mp_url = "https://www.mountainproject.com/route-finder?"
# 
# 
# &diffMaxrock=12400##
# &diffMinrock=1000##
# &is_sport_climb=1
# &is_trad_climb=1
# &is_top_rope=1
# &sort1=area
# &sort2=rating
# &pitches=0
# &stars=0
# &type=rock
# &viewAll=1
# &selectedIds=area_id
# =============================================================================