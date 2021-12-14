<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 14:21:48 2021

@author: Shaun
"""
import pandas as pd
import helper

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

FULL_DICT = BOULDER_DICT
FULL_DICT.update(YDS_DICT)

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

class Climber:
    def __init__(self, climber_soup, location_filter=None, sport_definition=['TR','Trad','Sport'], top_avg=10, clean=False):
        self.soup = climber_soup
        self.location_filter = location_filter

    def get_top_data(self, route_type, top=10, clean=False, route_col_name='Route Type'):
        if isinstance(route_type, list):
            route_filter = '|'.join(route_type)
        else:
            route_filter = route_type
        if clean:
            is_sends = self.clean_sends
        else:
            is_sends = self.sends
        top_routes = is_sends.loc[is_sends[route_col_name].str.contains(route_filter)]\
                             .sort_values(by='difficulty', axis=0, ascending=False)[:top].reset_index()
        
        if route_type=='Boulder':
            temp_dict = BOULDER_DICT
        else:
            temp_dict = YDS_DICT
            
        if not top_routes.empty:
            #I don't take top grade, I take first difficulty and convert. This is to remove trad protection rating and +/- for consistency
            best_grade =   list(temp_dict.keys())[list(temp_dict.values()).index(round(top_routes['difficulty'].iloc[0]))]
            top_avg_grade = list(temp_dict.keys())[list(temp_dict.values()).index(round(top_routes['difficulty'].mean()))]
        else:
            best_grade = "N/A"
            top_avg_grade = "N/A"
        return best_grade, top_avg_grade

    def to_df(self):
        d = {'name':[self.name],
             'best_lead_grade':[self.best_sport],
             'best_boulder_grade':[self.best_boulder],
             'top_ten_avg_lead_grade':[self.avg_sport],
             'top_ten_avg_boulder_grade':[self.avg_boulder],
             'location_filter':[self.location_filter],
             'tick_count':[self.tick_count]
             }
        return pd.DataFrame(d)

    def to_string(self):
        return self.name + ': Climbs:' + self.avg_sport + "/" + self.avg_boulder\
               + ". Has sent " + self.best_sport + "/" + self.best_boulder
    
    def split_exclude_char(self, text, split_chars, exclude_chars):
        if isinstance(split_chars, str):
            split_chars = [split_chars]
        if isinstance(exclude_chars, str):
            exclude_chars = [exclude_chars]
    
        split=1
        current_line=''
        split_list=[]
        for char in text:
            if char in exclude_chars:
                split=split*-1
            elif char in split_chars and split==1:
                split_list = split_list + [current_line]
                current_line=''
            else:
                current_line = current_line + char
        return split_list
    
class VL_Climber(Climber):
    
    def __init__(self, climber_soup, location_filter=None, sport_definition='Roped', top_avg=10, clean=False):
        super().__init__(climber_soup, location_filter, sport_definition, top_avg, clean)
        self.location_filter = location_filter
        self.soup = climber_soup
        self.name = self.soup.find("title").get_text()[:-1*len(' vertical-life profile')]
        self.unique_id = self.soup.find("meta", {"property":"al:ios:url"})['content'].split('/')[-1]
        self.sends = self.get_sends()
        self.clean_sends = self.sends
        self.best_sport, self.avg_sport = self.get_top_data(sport_definition, route_col_name='route_type')
        self.best_boulder, self.avg_boulder = self.get_top_data('Boulder', route_col_name='route_type')
        self.tick_count = len(self.sends)
    def get_sends(self):
        climb_list = self.soup.find_all(class_="route")
        columns = ['color', 'grade', 'difficulty', 'route_type', 'location']
        route_data = pd.DataFrame(columns = columns)
        if self.location_filter:
            climbs = [climb for climb in climb_list if self.location_filter in climb.get_text()]
        else:
            climbs = climb_list
        for climb in climbs:
            items = str(climb).split('\n')
            grade=items[2].split(" ")[-1]
            color=items[2].split(" ")[-2]
            location=items[5].split(">")[1].split('<')[0]
            if '5.' in climb.get_text() or '3-4' in climb.get_text():
                route_type = 'Roped'
                difficulty = YDS_DICT[grade]
            else:
                route_type = 'Boulder'
                difficulty = BOULDER_DICT[grade]
            route_data = helper.append_dataframes(route_data, pd.DataFrame([[color,grade,difficulty,route_type,location]], columns=columns))
        return route_data

class MP_Climber(Climber):

    def __init__(self, climber_soup, location_filter=None, sport_definition=['TR','Trad','Sport'], top_avg=10, clean=False, name=''):
        super().__init__(climber_soup, location_filter, sport_definition, top_avg, clean)
        self.name = name
        self.location_filter = location_filter
        self.soup = climber_soup

        self.sends, self.null_data = self.get_sends()
        if self.location_filter:
            self.sends = self.sends[self.sends['Location'].str.contains(self.location_filter)]
        self.clean_sends = self.sends
        self.clean_sends = self.clean_sends[~self.clean_sends['Lead Style'].str.contains('Fell')]
        self.clean_sends = self.clean_sends[~self.clean_sends['Lead Style'].str.contains('Hung')]
        
        self.best_sport, self.avg_sport = self.get_top_data(sport_definition, top=top_avg, route_col_name='Route Type')
        self.best_boulder, self.avg_boulder = self.get_top_data('Boulder', top=top_avg, clean=clean, route_col_name='Route Type')
        self.tick_count = len(self.sends)
        
    def get_sends(self):
        columns=['Date','Route','Rating','Notes','URL','Pitches','Location','Avg Stars',
                 'Your Stars','Style','Lead Style','Route Type','Your Rating','Length']
        send_data = pd.DataFrame(columns = columns)
        count=0
        for line in str(self.soup).split('\n'):
            if line!='':
                current_line = self.split_exclude_char(line, split_chars=[','], exclude_chars=['"','"'])
                if len(current_line)==14:
                    if count>0:
                        temp_send_data = pd.DataFrame([current_line], columns=columns)
                        send_data = send_data.append(temp_send_data)
            count=count+1
        send_data, null_data = self.add_send_difficulty(send_data)
        
        return send_data, null_data
            
    def add_send_difficulty(self, send_data):
        send_data['difficulty'] = send_data['Rating'].map(FULL_DICT)
        for i in range(5,1,-1): #Remove trad protection and +/-s to try to find a climb in dict
            null_map = send_data['difficulty'].isnull()
            if len(null_map)==0:
                break
            else:
                send_data.loc[null_map, 'difficulty'] = send_data.loc[null_map,'Rating'].str[:i].map(FULL_DICT)
        send_data = send_data[~send_data['difficulty'].isnull()]
        null_data = send_data[send_data['difficulty'].isnull()]
        return send_data, null_data
=======
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
>>>>>>> b90701d72deba963c9c77b3dbb306d6c953a8e72
