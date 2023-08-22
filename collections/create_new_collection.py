## Create new project in Flywheel
#   amf
#   Written Feb 19, 2021
#
#   Takes list of C-IDs and copies matching data that exists on Flywheel
#   into a new project via a collection

import flywheel
import csv

fw = flywheel.Client()

# create a collection if it doesn't already exist
collection = fw.collections.find_first('label=CBTN_D0125')
if not collection:
    collection_id = fw.add_collection({'label': 'CBTN_D0125'})
    collection = fw.get_collection(collection_id)

# import subject list from CSV
sub_list = []
filename = 'sub_list.csv'
with open(filename,'r') as data: 
   for row in csv.reader(data):
        sub_list.append(row[0])

# build out search query
query = ''
for sub in sub_list:
    if sub != sub_list[-1]:
        query += ''.join(['subject.label = ', sub,' OR '])
    else:
        query += ''.join(['subject.label = ', sub])

# run search
results = fw.search({'structured_query': query, 'return_type':'session'})

# add results to collection
for result in results:
    collection.add_sessions(result.session.id)
