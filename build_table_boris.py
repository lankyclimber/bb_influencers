import requests
import json
import pandas as pd

raw_table = pd.DataFrame.from_csv('Instagram Influencers.csv')
usernames = set(raw_table['Username'])

master_table = pd.DataFrame()

for u in usernames:
  r = requests.get("https://api.instagram.com/v1/users/search?q=%s&access_token=2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0" % u)
  if not r.ok:
    print ('arvind fail')
    continue
  user_dict = r.json()
  actual_user = list(filter(lambda v: v['username'] == u, user_dict['data']))
  if len(actual_user) > 0:
    master = requests.get("https://api.instagram.com/v1/users/%s/?access_token=2118157933.a8e8294.5bee2cbd51fd44c0a26eef435cac82e0" % actual_user[0]['id'])

    # place each individual's records into a table
    individual_data = pd.DataFrame(master.json())['data']

    # add individual's records into larger table
    master_table[actual_user[0]['id']] = individual_data

# invert the table to be more readable
master_table = master_table.T

# creates a new column named df_name on a dataframe named df, reaching
# into the counts column and pulling out relevant data named var_name
def pull_out_data(df, df_name, var_name):
  df[df_name] = master_table.counts.apply(lambda i: i.get(var_name, 'None Listed'))
  return df

# pull out some of the hidden information
pull_out_data(master_table, 'follows', 'follows')
pull_out_data(master_table, 'followed_by', 'followed_by')
pull_out_data(master_table, 'media', 'media')

# remove column that we don't need anymore
master_table.drop(labels=['counts'], axis=1, inplace=True)

print(master_table)
master_table.to_csv('master_instagram_table.csv')
