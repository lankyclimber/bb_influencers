import requests
import json
import pandas as pd
import collections
from collections import defaultdict
from geopy.geocoders import GoogleV3
#table=pd.DataFrame.from_csv('Instagram Influencers.csv')
#username=set(table['Username'])

access_token = '2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0'

#make method to input search parameters
media_count= 100
tag_search = ['cycling', 'rideyourbike', 'ridecolorado', 'coloradocyclist', 'coloradocycling', 'colorado', 'bikeporn', 'roadporn', 'ridetahoe', 'biketahoe']
caption_search = set()
cities = ['Denver, CO', 'Boulder, CO', 'South Lake Tahoe, CA', 'Aspen, CO', 'Glenwood Springs, CO', 'Carbondale, CO', 'Truckee, CA', 'Colorado Springs, CO']
tahoe_coord = [['38.939415', '-119.977399']]
aspen_coord = [['39.191031', '-106.818228']]

def retrieve_next_url (r, user_id_list, username_list):
    if 'next_url' in r.json()['pagination'].keys():
        user_id_list, username_list = retrieve_data_from_dict(r, user_id_list, username_list)
        pages = r.json()['pagination']
        next_url = pages['next_url']
        r = requests.get(next_url)
        retrieve_next_url (r, user_id_list, username_list)
    else:
        user_id_list, username_list = retrieve_data_from_dict(r, user_id_list, username_list)
    return user_id_list, username_list

def retrieve_data_from_dict(r, user_id_list, username_list):
    data_dict = r.json()['data']
    for dd in data_dict:
        user_id_list.append(dd['user']['id'])
        username_list.append(dd['user']['username'])
    return user_id_list, username_list

def retrieve_tagdata_from_dict(r, username, username_list):
    data_dict = r.json()['data']
    for dd in data_dict:
        username.add(dd['user']['username'])
        username_list.append(dd['user']['username'])
    return username, username_list

def retrieve_url (r, username, username_list):
    if 'next_url' in r.json()['pagination'].keys():
        username, username_list = retrieve_tagdata_from_dict(r, username, username_list)
        pages = r.json()['pagination']
        next_url = pages['next_url']
        r = requests.get(next_url)
        retrieve_url (r, username, username_list)
    else:
        username, username_list = retrieve_tagdata_from_dict(r, username, username_list)
    return username, username_list

def find_coord (cities):
    geolocator = GoogleV3()
    locations = pd.DataFrame (columns = ['Lat', 'Long', 'Place ID', 'User ID', 'Username'], index = cities)
    for c in cities:
        location = geolocator.geocode(c)
        locations.loc[c]['Lat'] = location.latitude
        locations.loc[c]['Long'] = location.longitude
    return locations

def loc_id (locations):
    for l in locations.index:
        loc_list = []
        r = requests.get("https://api.instagram.com/v1/locations/search?lat=%s&lng=%s&access_token=%s&count=100&distance=5000" % (locations.loc[l]['Lat'], locations.loc[l]['Long'], access_token))
        if not r.ok:
            continue
        loc_dict = r.json()['data']
        for place in loc_dict:
            loc_list.append(place['id'])
        locations.loc[l]['Place ID'] = loc_list
    return locations

def loc_media (locations):
    for l in locations.index:
        user_id_list = []
        username_list = []
        for place_id in locations.loc[l]['Place ID']:
            r = requests.get("https://api.instagram.com/v1/locations/%s/media/recent?access_token=%s&count=100&distance=5000" % (place_id, access_token))
            user_id_list, username_list = retrieve_next_url(r, user_id_list, username_list)
            locations.loc[l]['User ID'] = user_id_list
            locations.loc[l]['Username'] = username_list
    return locations

def build_loc_table (cities):
    locations = find_coord(cities)
    locations = loc_id(locations)
    locations = loc_media(locations)
    return locations

def tag_info (tags):
    total = pd.DataFrame(columns = ['Media Count'], index = tags)
    for tag in tags:
        r = requests.get("https://api.instagram.com/v1/tags/%s?access_token=%s" % (tag, access_token))
        if not r.ok:
            continue
        tag_dict = r.json()['data']
        total.loc[tag] = tag_dict['media_count']
    return total

def tag_to_username (tags):
    tag_df = tag_info(tags)
    username = set()
    username_list = []

    for i,j in tag_df.iterrows():
        r = requests.get("https://api.instagram.com/v1/tags/%s/media/recent?access_token=%s&count=%s" % (i, access_token,media_count))
        if not r.ok:
            continue
        username, username_list = retrieve_url(r, username, username_list)
    user_dict = {}
    username_series = pd.Series(username_list)
    for u in username:
        user_dict[u] = username_series.value_counts()[u]
    username_df = pd.DataFrame(columns = ['ID', 'Tag Count'], index = username)
    for user in username:
        username_df.loc[user]['Tag Count'] = user_dict[user]
    return username_df

def compare_usernames (loc_df, tag_df):
    loc_user_set = set()
    tag_user_set = set()
    user_set = set()
    for l in loc_df.index:
        for user in loc_df.loc[l]['User ID']:
            loc_user_set.add(user)
    for t in tag_df.index:
        tag_user_set.add(t)
    user_set = loc_user_set.intersection(tag_user_set)
    return user_set

#unordered set
def username_to_userid (username):
    userid_set = set()
    for u in username:
      r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=%s" % (u, access_token))
      if not r.ok:
        continue
      user_dict = r.json()['data']
      userid_set.add(r.json()['data'][0]['id'])
      username_set.add(u)
    media_table = pd.DataFrame(index = userid_set)
    return media_table

def pull_data (media_table, media_count):
    media_table['Username'] = None
    media_table['rct_media'] = None
    userid = media_table.index
    for u in userid:
        r = requests.get("https://api.instagram.com/v1/users/%s/media/recent/?access_token=%s&count=%s" % (u, access_token, media_count))
        if not r.ok:
            continue
        media_table.loc[u]['rct_media'] = r.json()['data']
        media_table.loc[u]['Username'] = media_table.loc[u]['rct_media']['username']
    #return media_table

    #DO THESE NEED TO RETURN ANYTHING OR DO I JUST SET THE TABLE EQUAL TO CALLING THE METHOD

def count (media_table, existing_key, new_key):
    total = None
    for x in media_table['rct_media']:
        total += x[existing_key]['count']
    media_table[new_key] = total
    #return media_table[new_key]

def counts (media_table, existing_key, new_key):
    total = None
    for x in media_table['rct_media']:
        total += x['counts'][existing_key]
    media_table[new_key] = total
    #return media_table[new_key]

def text (media_table, existing_key, new_key):
    total = None
    for x in media_table['rct_media']:
        total += x[existing_key]['text'] + ' '
    media_table[new_key] = total
    #return media_table[new_key]

def average (media_table, key_1, key_2):
    new_key = 'Average ' + key_1 + 'per' + key_2
    media_table[new_key] = None
    userid = media_table.index
    for u in userid:
        media_table.loc[u][new_key] = media_table.loc[u][key_1]/media_table.loc[u][key_2]
    #return media_table[new_key]

def search_tags (media_table, tag_search):
    media_table['Used Tags'] = []
    userid = media_table.index
    for u in userid:
        for tag in media_table.loc[u]['rct_tags']:
            for t in tag_search:
                if tag.lower() == t.lower():
                    m['BB_tag_list'].append(tag)            
    #return media_table

def search_caption (media_table, caption_search):
    media_table['Used Text'] = []
    userid = media_table.index
    for u in userid:
        for text in media_table.loc[u]['caption_text']:
            if text in caption_search:
                media_table.loc[u]['Used Text'].append(text + ' ')
    #return media_table

def organize(username):
    media_table = username_to_userid(username)
    pull_data (media_table, media_count)
    #media_table['nmb_cmnts'] = media_table.rct_media.apply(lambda i: pull_out_data(media_table, 'comments', 'count', 'nmb_cmnts'))
    count (media_table, 'comments', 'Number of Comments')
    count (media_table, 'likes', 'Number of Likes')
    text (media_table, 'caption', 'Caption Text')
    counts (media_table, 'follows', 'Follows')
    counts (media_table, 'followed_by', 'Followed By')
    counts (media_table, 'media', 'Posts')
    average (media_table, 'Number of Likes', 'Posts')
    average (media_table, 'Number of Comments', 'Posts')
    search_tags (media_table, tag_search)
    search_caption (media_table, caption_search)
    return media_table

#media_table = organize(['lankyclimber', 'beccaskinner'])
#print (media_table)

'''
#shelved methods
def pull_out_data(media_table, existing_key, sec_key, new_key):
    total = None
    for x in media_table['rct_media']:
        #not sure the correct keyword for null
        if sec_key == null:
            total += x[existing_key]
        else:
            total += x[existing_key][sec_key]
    media_table[new_key] = total
    return media_table[new_key]

def search (media_table, search_params, name):
#seems like the proper place for a defaultdict that defaults to 1 rather than a list, then counts everytime the word is reused
    media_table[name] = []


def filter_loc (media_table, locs):
    media_table[loc] = []
'''


#START COMMANDS
locations = build_loc_table(cities)
tag_df = tag_to_username(tag_search)
print (tag_df)
media_table = organize(compare_usernames(locations, tag_df))
print (media_table)
#media_table.to_csv('instagram_media_table.csv')
