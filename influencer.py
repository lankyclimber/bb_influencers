import pandas as pd
table=pd.DataFrame.from_csv('Instagram Influencers.csv')
table.describe()
print table
print table()
table
table.head(5)
set(table['Username'])
username=set(table['Username'])
