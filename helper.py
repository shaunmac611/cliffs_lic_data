# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 09:02:06 2021

@author: Shaun
"""
import validators
import urllib.request as url_request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from http.client import IncompleteRead

def is_climb_url(site):
    if 'href=' in site:
        site = site.split('href=')[1].split('>')[0][1:-1]
    if validators.url(site):
        try:
            user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            headers={'User-Agent':user_agent,} 
            request = url_request.Request(site,None,headers)
            webUrl = url_request.urlopen(request)
            climb_soup = BeautifulSoup(webUrl, 'html.parser')
            return climb_soup
        except HTTPError:
            return False
        except IncompleteRead:
            return False
    else:
        return False

def append_dataframes(big_df, small_df):
    if big_df.empty:
        big_df = small_df.copy()
    else:
        big_df = big_df.append(small_df)
    return big_df
