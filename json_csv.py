import json
from csv import DictWriter

json_data = json.load(open('data.json'))
writer = DictWriter(open('data.csv', 'w'),extrasaction='ignore', fieldnames = json_data[0].keys())
writer.writeheader()
writer.writerows(json_data)