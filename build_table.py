import requests
import json
import pandas as pd
table=pd.DataFrame.from_csv('Instagram Influencers.csv')
username=set(table['Username'])

user_data=[]
for u in username:
  r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0" % u)
  if not r.ok:
    print ('arvind fail')
    continue
  user_dict = r.json()
  actual_user = list(filter(lambda v: v['username'] == u, user_dict['data']))
  if len(actual_user) > 0:
    #print ("username: %s" % u)
    #print ("user id: %s" % actual_user[0]['id'])
    master = requests.get("https://api.instagram.com/v1/users/%s/?access_token=2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0" % actual_user[0]['id'])
    user_data.append(master.json()['data'])

json.dump(user_data,open('data.json','w'))