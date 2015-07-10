import requests
import json
import pandas as pd
from sets import sets
from collections import defaultdict
table=pd.DataFrame.from_csv('Instagram Influencers.csv')
username=set(table['Username'])

master_media = pd.DataFrame()
user_tags = pd.DataFrame()
access_token = '2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0'

#make method to input search parameters
media_count= 10
tag_search =Set([])

username = ['beccaskinner']


#break into method that separates requests from individual column creation
def make_data_table (username):
    master_table = pd.DataFrame()
    for u in username:
      r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=%s" % (u, access_token))
      if not r.ok:
        print ('User %s does not exist.' % u)
        continue
      user_dict = r.json()
      actual_user = list(filter(lambda v: v['username'] == u, user_dict['data']))
      master_table.append(actual_user)
      userid_list = master_table['id']
      return master_table, userid_list

def build_table (users, userid, media_count):
    recent_media = userid
    #load table into df
    #timestamp for each user
    media = defaultdict(lambda: defaultdict(int))
    for u in userid:
        request = requests.get("https://api.instagram.com/v1/users/%s/media/recent/?access_token=%s&count=%s" % (u, access_token, media_count))
        if not request.ok:
            continue
        recent_media = json.loads(request.json)
        #should most recent first
        #change logic to read previous output
        for m in reversed(recent_media['data']):
            if m['id'] == latest_id:
                break
            media[u]['nmb_cmnts'] += m['comments']['count']
            media[u]['nmb_likes'] += m['likes']['count']
            media[u]['nmb_posts'] += 1
            media[u]['caption_text'] += m['text'] + ' '
        media[u]['avg_comments'] = media[u]['nmb_cmnts'] / media[u]['nmb_posts']

        #media_data = pd.DataFrame(recent_media.json()['data'])
        #media_data['user_id'] = individual_data.id
        #media_data['nmb_cmmts'] = media_data.comments.apply(lambda i: i['count'])
        #media_data['nmb_likes'] = media_data.likes.apply(lambda i: i['count'])
        #media_data['caption_text'] = media_data.caption.apply(lambda i: i['text'])
        individual_data['Posts'] = len(media_data)
        #make into apply with groupby
        individual_data['rct_comments'] = media_data.groupby(['user_id']).nmb_cmmts.sum().get_value(0)
        individual_data['avg_comments'] = media_data.groupby(['user_id']).nmb_cmmts.mean().get_value(0)    
        individual_data['rct_likes'] = media_data.groupby(['user_id']).nmb_likes.sum().get_value(0)
        individual_data['avg_likes'] = media_data.groupby(['user_id']).nmb_likes.mean().get_value(0)
        individual_data['rct_tags'] = Set([])
        individual_data['BB_tag_match'] = ''
        individual_data['BB_tag_list'] = []

    user_tags = media_data.tags
    for index, tags in enumerate(user_tags):
        list_tags = Set(user_tags.get_value(index))
        for tag in list_tags:
            individual_data['rct_tags'].append(tag)


    #should make into method search_tags (method or script?)
    #need to include medias index number for tag
    #will want to do a text search on captions for strictly brand names as well in case people don't use tags if user_tags.getvalue() < posts...
    #python function 'in' 'cat' in 'cat in hat'   .lower and .trim
def search_tags (user, tag_search):
    for u in user:
        for tag in u['rct_tags']:
            for t in tag_search:
                if tag.lower() == t.lower():
                    u['BB_tag_match'] = 'Yes'
                    u['BB_tag_list'].append(tag)            
        if u['BB_tag_match']  != 'Yes':
            u['BB_tag_match'] = 'No'
    return user
#these are now in the wrong header, master_table not longer fits
    master_table[actual_user[0]['id']] = individual_data
    master_media=master_media.append(media_data, ignore_index=True)

# invert the table to be more readable
master_table = master_table.T

#need to reorder columns, exclude index
# creates a new column named df_name on a dataframe named df, reaching
# into the counts column and pulling out relevant data named var_name
def pull_out_data(df, df_name, var_name):
  df[df_name] = master_table.counts.apply(lambda i: i.get(var_name, 'None Listed'))
  return df

# pull out some of the hidden information
pull_out_data(master_table, 'follows', 'follows')
pull_out_data(master_table, 'followed_by', 'followed_by')
pull_out_data(master_table, 'media', 'media')

master_table.drop(labels=['counts','code'], axis=1, inplace=True)
master_table.rename(columns={'id':'User Id'}, inplace=True)
master_table.set_index('User Id', inplace=True)
master_table.to_csv('master_instagram_table.csv')
