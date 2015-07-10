import requests
import json
import pandas as pd
from sets import Set
table=pd.DataFrame.from_csv('Instagram Influencers.csv')
username=set(table['Username'])
master_table = pd.DataFrame()
access_token = '2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0'
follows_min = 50
follows_max = 10000000
followed_by_min = 1000
followed_by_max = 10000000

#collect everyone's follows/followers
#username to userid
#userid return attributes
#userid to username
#read on sets (lists with unique values)

def grow_id_from_id (user_id):
    follow_id_list = []
    followed_by_id_list = []
    for u in user_id:
        raw_follows = requests.get("https://api.instagram.com/v1/users/%s/follows/?access_token=%s" %  (u, access_token))
        raw_followed_by = requests.get("https://api.instagram.com/v1/users/%s/followed-by/?access_token=%s" %  (u, access_token))
        data_follows = pd.DataFrame(raw_follows.json()['data'])
        data_followed_by = pd.DataFrame(raw_followed_by.json()['data'])   
        for d in data_follows:     
            follow_id_list += d['id']
        for d in data_followed_by:
            followed_by_id_list += d['id']
    print (follow_id_list, ' ', followed_by_id_list)
    master_set = set{}
    master_set.update(follow_id_list, followed_by_id_list)
    return master_set

def grow_id_from_username (username):
    follow_id_list = []
    followed_by_id_list = []
    for u in username:
        r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=%s" % (u, access_token))
        user_dict = r.json()
        actual_user = list(filter(lambda v: v['username'] == u, user_dict['data']))
        raw_follows = requests.get("https://api.instagram.com/v1/users/%s/follows/?access_token=%s" % (actual_user[0]['id'], access_token))
        data_follows = pd.DataFrame(raw_follows.json()['data'])
        raw_followed_by = requests.get("https://api.instagram.com/v1/users/%s/followed-by/?access_token=%s" % (actual_user[0]['id'], access_token))
        data_followed_by = pd.DataFrame(raw_followed_by.json()['data'])
        for d in data_follows:     
            follow_id_list += d['id']
        for d in data_followed_by:
            followed_by_id_list += d['id']
    print (follow_id_list, ' ', followed_by_id_list)
    master_set = set{}
    master_set.update(follow_id_list, followed_by_id_list)
    return master_set

def id_filter (id_set):
    follows_min = input('follows_min: ')
    follows_max = input('follows_max: ')
    followed_by_min = input('followed_by_min: ')
    followed_by_max = input('followed_by_max: ')
    master_set = set{}

    for i in id_set:
        r = requests.get("https://api.instagram.com/v1/users/%s/?access_token=%s" % (i, access_token))
        if r.ok:
            user_dtb = pd.DataFrame(r.json()['data'])
            if user_dtb['media'] > 0 && user_dtb['follows'] > follows_min && user_dtb['follows'] < follows_max && user_dtb['followed_by'] > followed_by_min && user_dtb['followed_by'] < followed_by_max:
                master_set += i
    return master_set