# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 17:41:26 2021

@author: Shaun

Potential Improvements:
    Add Climber link to object
"""
import pandas as pd

import helper
from climb import MP_Climb
from climber import MP_Climber

location_dict = {'Red River Gorge':'105841134', 'New River Gorge':'105855991',
                 'Yosemite':'105833388', 'Gunks':'105798167', 'Boulder Canyon':'105744222',
                 'Joshua Tree':'105720495', 'Eldorado Canyon':'105744246', 'Rumney':'105867829',
                 'Red Rocks':'105731932'}
def test_main():
    for location in ['Boulder Canyon', 'Red Rocks', 'Rumney', 'Eldorado Canyon', 'Yosemite']:
        location_code = location_dict[location]
        print('Pulling Data for: ' + location)
        climb_data, climber_data = loop_through_areas(location_code, location)

def loop_through_areas(location_code, location, climb_data=pd.DataFrame(), climber_data=pd.DataFrame(), pull_climber_data=True):
    soup = helper.is_climb_url(get_mp_link(location_code))
    if soup:
        climb_total = int(soup.find_all(class_="float-md-left")[0].get_text().split('Results 1 to ')[1].split(' of')[0])
        if climb_total<1000:
            climb_data, climber_data = loop_through_climbs(soup, location, location_code, pull_climber_data, climb_total)
        else:
            soup_parent = helper.is_climb_url("https://www.mountainproject.com/area/" + location_code)
            if soup_parent:
                areas = soup_parent.find_all(class_="lef-nav-row")
                area_links = [i.find_all('a')[0] for i in areas]
                for area_link in area_links:
                    location_code = area_link.get('href').split('/')[4]
                    print(area_link.get('href').split('/')[5])
                    area_data, area_climber_data = loop_through_areas(location_code, location, climb_data, climber_data, pull_climber_data)
                    climb_data = helper.append_dataframes(climb_data, area_data)
                    climber_data = helper.append_dataframes(climber_data, area_climber_data)
                    climb_data.to_excel(location+'_climbs.xlsx')
                    climber_data.to_excel(location+'_climbers.xlsx')
    return climb_data, climber_data

def loop_through_climbs(soup, location, location_code, pull_climber_data, climb_total, constant_export = False, suppress_print=False):
    climb_data = pd.DataFrame()
    climber_data = pd.DataFrame()
    link_list = []
    count=0
    for link in soup.find_all('a'):
        if not(link.get('href') is None) and ('/route/' in link.get('href')) and (count<climb_total):
            count=count+1
            climb_soup = helper.is_climb_url(str(link.get('href')))
            if climb_soup:
                route = MP_Climb(climb_soup)
                if pull_climber_data:
                    climber_data, link_list = get_ascent_data(route, climber_data,
                                                              link_list, location,
                                                              constant_export,
                                                              True)
                climb_data = helper.append_dataframes(climb_data, route.to_df())
                if constant_export:
                    climb_data.to_excel(location+'_climbs_'+location_code+'.xlsx', index=False)
                if count>0 and count%50==0 and not suppress_print:
                    print('=====Climb Count: ' + str(count))
    return climb_data, climber_data

def get_ascent_data(route, climber_data, link_list, location, constant_export, suppress_print):
    climber_count=0
    soup = helper.is_climb_url(route.ascents_link)
    if soup:
        tick_options = soup.find_all(class_="table table-striped")
        if len(tick_options)>=4:
            ticks = tick_options[3]
            climber_links = ticks.find_all('a')
            for link in climber_links:
                if not (link in link_list):
                    link_list = link_list + [link]
                    climber_soup = helper.is_climb_url(link.get('href')+'/tick-export')
                    climber_o = MP_Climber(climber_soup, name=link.get_text(), location_filter=location)
                    climber_data = helper.append_dataframes(climber_data, climber_o.to_df())
                    climber_count=climber_count+1
                    if constant_export:
                        climber_data.to_excel(location+'_climbers_temp.xlsx', index=False)
                    if climber_count> 0 and climber_count%250==0 and not suppress_print:
                        print('Climber Count: ' + str(climber_count) + ', ', end=' ')
    return climber_data, link_list

def get_mp_link(area_id, climb_filter=['sport','trad','tr']):
    climb_filter = [i.lower() for i in climb_filter]
    mp_link = "https://www.mountainproject.com/route-finder?&selectedIds=" + area_id
    if 'sport' in climb_filter:
        mp_link = mp_link + "&is_sport_climb=1"
    if 'trad' in climb_filter:
        mp_link = mp_link + "&is_trad_climb=1"
    if 'tr' in climb_filter or 'top rope' in climb_filter:
        mp_link = mp_link + "&is_top_rope=1"
    #Will search all rock climbs between 5.0 and 5.15d with any stars or pitches
    mp_link = mp_link + "&diffMaxrock=12400&diffMinrock=1000&sort1=area&sort2=rating&pitches=0&stars=0&type=rock&viewAll=1"
    return mp_link
