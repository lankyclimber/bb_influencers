import requests
import json
import pandas as pd
table=pd.DataFrame.from_csv('Instagram Influencers.csv')
username=set(table['Username'])
master_table = pd.DataFrame()
access_token = '2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0'
degree = 1
from_gen = 0
follows_min = 50
follows_max = 10000000
followed_by_min = 1000
followed_by_max = 10000000

username=['beccaskinner','lankyclimber']
for i in range(degree):
    #for key,item in username:  username needs to be a dict with key = username and item =generation added to list
    #then set conditional based upon variable from_gen as a starting point.  Current users will be gen 0. 
    #feels important to track when people are added
    master = pd.DataFrame()
    for u in username:
      r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=%s" % (u, access_token))
      if not r.ok:
        print ('arvind fail')
        continue
      user_dict = r.json()
      actual_user = list(filter(lambda v: v['username'] == u, user_dict['data']))
      if len(actual_user) > 0:
        #not sure these two lines are needed
        user = requests.get("https://api.instagram.com/v1/users/%s/?access_token=%s" % (actual_user[0]['id'], access_token))
        user_dtb = pd.DataFrame(user.json())['data']

        follows_raw = requests.get("https://api.instagram.com/v1/users/%s/follows/?access_token=%s" % (actual_user[0]['id'], access_token))
        follows_dict = follows_raw.json()
        follows_id = list(filter(lambda v: v['id'] == actual_user[0]['id'], follows_dict['data']))
        print (follows_id)
        followed_by_raw = requests.get("https://api.instagram.com/v1/users/%s/followed_by/?access_token=%s" % (actual_user[0]['id'], access_token))
        followed_by_dict = followed_by_raw.json()['data']
        followed_by_id = followed_by_dict['id']
        print (followed_by_id)

        def new_id_from_id (user_id, var_name):
            for u in user_id:
                raw = requests.get("https://api.instagram.com/v1/users/%s/%s/?access_token=%s" %  (u, var_name, access_token))
                data = pd.DataFrame(raw.json()['data'])
                #ideally this would be named var_name_id
                ids = data['id']

        def new_id_from_username (username, var_name):
            for u in username:
                r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=%s" % (u, access_token))
                user_dict = r.json()
                actual_user = list(filter(lambda v: v['username'] == u, user_dict['data']))
                raw = requests.get("https://api.instagram.com/v1/users/%s/%s/?access_token=%s" % (actual_user[0]['id'], var_name, access_token))
                data = pd.DataFrame(raw.json()['data'])
                #ideally this would be named var_name_id
                ids = data['id']

        #master_table = follows_id + followed_by_id

        for m in master_table:
            r = requests.get("https://api.instagram.com/v1/users/%s/?access_token=%s" % (m, access_token))
            if not r.ok:
                master_table.drop(m)
                continue
            user = r.json()
            user_dtb = pd.DataFrame(user.json())['data']
            if user_dtb['counts']['follows'] < follows_min or user_dtb['counts']['follows'] > follows_max or user_dtb['counts']['followed_by'] < followed_by_min or user_dtb['counts']['followed_by'] > followed_by_max:
                master_table.drop(m)
            #this needs to be conditional upon m still being in master_table
            master.append(user_dtb['username'])
        # = second_degree.append(follows.json()['data']['id'] 
        #second_degree = second_degree.append(followed_by.json())['data']['id'])

        #for s in second_degree:
            #individual_data = requests.get("https://api.instagram.com/v1/users/%s/?access_token=%s" % s, access_token)
    #username = username +  master

for u in username:
    r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=%s" % (u, access_token))
    user_dict = pd.DataFrame(r.json()['data'])
    print (user_dict['id'])
    print (master_table)
#master_table.to_csv('instagram_users.csv')