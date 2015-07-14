import requests
import json
import pandas as pd
from collections import defaultdict
from geopy.geocoders import Nominatim
#table=pd.DataFrame.from_csv('Instagram Influencers.csv')
#username=set(table['Username'])

access_token = '2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0'

#make method to input search parameters
media_count= 10
tag_search = set(['cycling', 'rideyourbike', 'ridecolorado', 'coloradocyclist', 'coloradocycling', 'colorado', 'bikeporn', 'roadporn', 'ridetahoe', 'biketahoe'])
caption_search = set()
cities = ['Denver, CO', 'Boulder, CO', 'South Lake Tahoe, CA', 'Aspen, CO', 'Glenwood Springs, CO', 'Carbondale, CO', 'Truckee, CA', 'Carson City, CA', 'Reno, CA', 'Colorado Springs, CO']
tahoe_coord = [['38.939415', '-119.977399']]
aspen_coord = [['39.191031', '-106.818228']]

def find_coord (cities):
    geolocator = Nominatim()
    locations = pd.DataFrame (columns = ['Lat', 'Long', 'Place ID', 'User ID', 'Username'], index = cities)
    for c in cities:
        loc = geolocator.geocode(c)
        locations.loc[c]['Lat'] = loc.latitude
        locations.loc[c]['Long'] = loc.longitude
    return locations

#should just attach id to locations df
def loc_id (locations):
    for l in locations:
        r = requests.get("https://api.instagram.com/v1/locations/search?lat=%s&lng=%s&access_token=%s&count=100&distance=5000" % (l['Lat'], l['Long'], access_token))
        if not r.ok:
            continue
        loc_dict = pd.DataFrame(r.json()['data'])
        locations.loc[l]['Place ID'] = loc_dict['id']
    print (locations)
    return locations

def loc_media (locations):
    for l in locations:
        r = requests.get("https://api.instagram.com/v1/locations/%s/media/recent?access_token=%s&count=100&distance=5000" % (l['Place ID'], access_token))
        if not r.ok:
            continue
        data_dict = pd.DataFrame(r.json()['data'])
        for dd in data_dict:
            print (dd)
            locations.loc[l]['User Id'].append(dd['id'])
            locations.loc[l]['Username'].append(dd['username'])
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

tag_count = tag_info(tag_search)
print (tag_count)

def tag_to_username (tags):
    tag_count = tag_info(tags)
    username = set()
    for i,j in tag_count.iterrows():
        print ("I: ", i)
        print ("J: ",  j)
        if j['Media Count'] < 1000:
            r = requests.get("https://api.instagram.com/v1/tags/%s/media/recent?access_token=%s" % (i, access_token))
            if not r.ok:
                continue
            tag_dict = r.json()['data']
            for t in tag_dict:
                username.add(t['user']['username'])
    return username

username = tag_to_username(tag_search)
print (username)

def compare_usernames (loc_df, tag_users):
    loc_user_set = set()
    composite_user_set = set()
    final_user_set = set()
    for l in loc_df:
        loc_user_set.add(loc_df.loc[l]['User ID'])
    composite_user_set.add(loc_user_set, tag_users)
    for user in composite_user_set:
        if user in loc_user_set && user in tag_users:
            final_user_set.add(user)
    return final_user_set

def username_to_userid (username):
    userid_set = set()
    username_set = set()
    for u in username:
      r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=%s" % (u, access_token))
      if not r.ok:
        continue
      user_dict = r.json()['data']
      userid_set.add(r.json()['data'][0]['id'])
      username_set.add(u)
      print (userid_set)
    media_table = pd.DataFrame(index = userid_set)
    media_table['Username'] = username_set

    return media_table

def pull_data (media_table, media_count):
    media_table['rct_media'] = None
    userid = media_table.index
    for u in userid:
        r = requests.get("https://api.instagram.com/v1/users/%s/media/recent/?access_token=%s&count=%s" % (u, access_token, media_count))
        if not r.ok:
            continue
        media_table.loc[u]['rct_media'] = r.json()['data']
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
    r#eturn media_table

def search_caption (media_table, caption_search):
    media_table['Used Text'] = []
    userid = media_table.index
    for u in userid:
        for text in media_table.loc[u]['caption_text']:
            if text in caption_search
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

media_table = organize(['lankyclimber', 'beccaskinner'])
print (media_table)



#shelved methods
def pull_out_data(media_table, existing_key, sec_key, new_key):
    total = None
    for x in media_table['rct_media']:
        #not sure the correct keyword for null
        if sec_key == null:
            total += x[existing_key]
        else;
            total += x[existing_key][sec_key]
    media_table[new_key] = total
    return media_table[new_key]

def search (media_table, search_params, name):
#seems like the proper place for a defaultdict that defaults to 1 rather than a list, then counts everytime the word is reused
    media_table[name] = []


def filter_loc (media_table, locs):




#START COMMANDS
coordinates = find_coord(cities)

#these are now in the wrong header, master_table not longer fits
    master_table[actual_user[0]['id']] = individual_data
    master_media=master_media.append(media_data, ignore_index=True)

# invert the table to be more readable
master_table = master_table.T

#need to reorder columns, exclude index
# creates a new column named df_name on a dataframe named df, reaching
# into the counts column and pulling out relevant data named var_name


master_table.drop(labels=['counts','code'], axis=1, inplace=True)
master_table.rename(columns={'id':'User Id'}, inplace=True)
master_table.set_index('User Id', inplace=True)
master_table.to_csv('master_instagram_table.csv')
