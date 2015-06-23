import requests
import json
import pandas as pd
table=pd.DataFrame.from_csv('Instagram Influencers.csv')
username=set(table['Username'])
master_table = pd.DataFrame()
master_media = pd.DataFrame()
user_tags = pd.DataFrame()
access_token = '2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0'

#search parameters
media_count= 10
tag_search =['yeti','lasportiva','flyfishing','trailrunning', 'ope']

username = ['beccaskinner']

for u in username:
  r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=%s" % (u, access_token))
  if not r.ok:
    print ('User %s does not exist.' % u)
    #end loop command needed, move to next u
    continue
  user_dict = r.json()
  actual_user = list(filter(lambda v: v['username'] == u, user_dict['data']))
  if len(actual_user) > 0:
    #manipulates individual_data 
    master = requests.get("https://api.instagram.com/v1/users/%s/?access_token=%s" % (actual_user[0]['id'], access_token))
    recent_media = requests.get("https://api.instagram.com/v1/users/%s/media/recent/?access_token=%s&count=%s" % (actual_user[0]['id'], access_token, media_count))
    individual_data = pd.DataFrame(master.json())['data']
    media_data = pd.DataFrame(recent_media.json()['data'])
    media_data['user_id'] = individual_data.id
    media_data['nmb_cmmts'] = media_data.comments.apply(lambda i: i['count'])
    media_data['nmb_likes'] = media_data.likes.apply(lambda i: i['count'])
    media_data['caption_text'] = media_data.caption.apply(lambda i: i['text'])
    print (media_data['caption_text'])
    individual_data['Posts'] = len(media_data)
    individual_data['rct_comments'] = media_data.groupby(['user_id']).nmb_cmmts.sum().get_value(0)
    individual_data['avg_comments'] = media_data.groupby(['user_id']).nmb_cmmts.mean().get_value(0)    
    individual_data['rct_likes'] = media_data.groupby(['user_id']).nmb_likes.sum().get_value(0)
    individual_data['avg_likes'] = media_data.groupby(['user_id']).nmb_likes.mean().get_value(0)
    individual_data['rct_tags'] = []
    individual_data['BB_tag_match'] = ''
    individual_data['BB_tag_list'] = []
    
    #will eventually want to make this into a dict as well to store a count
    #also will want to give each tag an index to refer back to its post of origin, be able to provide vitals for that post in a separate sheet, much like cision hits

    user_tags = media_data.tags
    for index, tags in enumerate(user_tags):
        list_tags = user_tags.get_value(index)
        for i, tag in enumerate(list_tags):
            #need a way to de-dupe
            individual_data['rct_tags'].append(tag)


    #needs refinements to make spaces and caps irrelevant
    #should make into method search_tags (method or script?)
    #need to include medias index number for tag
    #will want to do a text search on captions for strictly brand names as well in case people don't use tags if user_tags.getvalue() < posts...
    for tag in individual_data['rct_tags']:
        for t in tag_search:
            if tag == t:
                individual_data['BB_tag_match'] = 'Yes'
                individual_data['BB_tag_list'].append(tag)            
    if individual_data['BB_tag_match']  != 'Yes':
        individual_data['BB_tag_match'] = 'No'

    #this adds an extra column without a heading to master_table accidentaly 
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

master_table.to_csv('master_instagram_table.csv')