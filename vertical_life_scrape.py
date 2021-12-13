# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 19:00:44 2021

@author: Shaun
"""
import pandas as pd

import helper
from climb import VL_Climb
from climber import VL_Climber

def full_cliffs_scrape():
    climb_data_df = cliffs_climb_scrape("https://www.vertical-life.info",
                                        "/en/indoor/the-cliffs-at-lic/")
    climb_data_df.to_excel('cliffs_climbs.xlsx')
    
    _ = cliffs_climber_scrape("https://www.vertical-life.info",
                              "/en/indoor/the-cliffs-at-lic/")

"""Pull Climb Data"""
def cliffs_climb_scrape(core_site, area_site):
    soup = helper.is_climb_url(core_site + area_site)

    tables = soup.find_all('table')
    roped = tables[2].find_all(class_="route")
    boulders = tables[3].find_all(class_="route")
        
    roped_data = loop_through_climbs(roped, 'roped', core_site)
    boulder_data = loop_through_climbs(boulders, 'boulder', core_site)
    climb_data_df = roped_data.append(boulder_data)
    return climb_data_df

def loop_through_climbs(routes, climb_type, core_site):
    route_data = pd.DataFrame()
    for route in routes:
        climb_url = route.find_all('a')
        if len(climb_url)>0:
            climb_soup = helper.is_climb_url(core_site + climb_url[0].get('href'))
            if climb_soup != False:
                climb = VL_Climb(climb_soup, climb_type)
                route_data = helper.append_dataframes(route_data, climb.to_df())
    return route_data

"""Pull Climber Data"""
def cliffs_climber_scrape(core_site, area_site, constant_export=True, suppress_print=False):
    soup = helper.is_climb_url(core_site+area_site)
    climber_data = pd.DataFrame()
    count=0
    for link in soup.find_all('a'):
        if ('/en/climbers/' in link.get('href')) and (not '\n\n\n\n\n' in link.get_text()):
            count=count+1
            if count>20:
                climber_soup = helper.is_climb_url(core_site + str(link.get('href')))
                if climber_soup != False and climber_soup.find("title").get_text()!='Worldwide Climbing and Training | Vertical-Life Climbing':
                    climber_o = VL_Climber(climber_soup, location_filter='The Cliffs at LIC')
                    climber_data = helper.append_dataframes(climber_data, climber_o.to_df())
                    if constant_export:
                        climber_data.to_excel('cliffs_climbers.xlsx', index=False)
                    if count%100==0 and not suppress_print:
                        print('Climber Count: ' + str(count))
    return climber_data
