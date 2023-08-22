# issue encountered: limiting to 1000 rows in returned DF
#   larger data views in browser break
#
#   for each session in the project:
#       - compiles a list of acquisitions in the session
#           but if it's empty (no files), delete it
#       - for each acquisition:
#           -- check for matching SeriesNumber in the list of all acquisitions
#           -- if there's 1 matching SeriesNum:
#               -- if their labels have a fuzzy match > 90 then delete one of them (after replacing spaces with underscore)
#                   deletes the acq with fewer files, otherwise deletes the newer acquisition
#
#  could have issue if > 2 matching acq's in a session based on series-number, but a subset of them are duplicates
#  duplicate acq's are due to differences in spaces and underscores

# project_label = 'LGG_SB_pilot'
# fw_group = 'flywheel'
project_label = 'ATRT'
fw_group = 'd3b'
project_label = []

import flywheel
import pandas as pd
from fuzzywuzzy import fuzz,process
from operator import itemgetter

fw = flywheel.Client() # d3b dev

grp_cntnr = fw.lookup(fw_group)

out_list = []
if project_label==[]:
    for proj in grp_cntnr.projects(): # fw.projects() returns list of proj's
        print(proj.label)
        project_label.append(proj.label)

for proj in project_label:
    proj_cntnr = grp_cntnr.projects.find_first(f'label={proj}')
    for sub in proj_cntnr.subjects():
        for ses in sub.sessions():
            acq_labels=[]
            acq_ids=[]
            acq_nFiles=[]
            acq_SeriesNums=[]
            acq_created=[]
            # compile a list of all acquisitions in the session
            for acq in ses.acquisitions.iter():
                # if there are no files in the acquisition, delete it
                if len(acq.files) == 0:
                    fw.delete_acquisition(acq.id)
                # otherwise add it to the list
                else:
                    label = acq.label
                    acq_labels.append(label)
                    acq_ids.append(acq.id)
                    acq_nFiles.append(len(acq.files))
                    acq_SeriesNums.append(label.split(' - ')[0])
                    acq_created.append(acq.created.date())
            # now check for duplicates by looping through all acquisitions in this session
            for series_num in acq_SeriesNums:
                indices = [i for i, x in enumerate(acq_SeriesNums) if x == series_num] # find matching SeriesNum
                if len(indices) == 2:
                    match_labels = itemgetter(*indices)(acq_labels)
                    match_ids = itemgetter(*indices)(acq_ids)
                    match_nFiles = itemgetter(*indices)(acq_nFiles)
                    match_created = itemgetter(*indices)(acq_created)
                    # print(match_labels)
                    acq1 = match_labels[0].replace(' ','_')
                    acq2 = match_labels[1].replace(' ','_')
                    if (fuzz.ratio(acq1[0:-1], acq2[0:-1]) >= 90) & (match_labels[0] != 'Files'):
                        # delete the acq with less files than the other
                        if match_nFiles[0] < match_nFiles[1]:
                            try:
                                fw.delete_acquisition(match_ids[0])
                                # out_list.append([match_labels[0], match_labels[1], \
                                                 # match_nFiles[0], match_nFiles[1]])
                            except:
                                continue
                        elif match_nFiles[0] > match_nFiles[1]:
                            try:
                                fw.delete_acquisition(match_ids[1])
                                # out_list.append([match_labels[1], match_labels[0], \
                                                 # match_nFiles[1], match_nFiles[0]])
                            except:
                                continue
                        elif match_nFiles[0] == match_nFiles[1]:
                            if match_created[0] < match_created[1]: # delete the newer acq
                                try:
                                    fw.delete_acquisition(match_ids[1])
                                    # out_list.append([match_labels[1], match_labels[0], \
                                                     # match_created[1], match_created[0]])
                                except:
                                    continue
                            elif match_created[1] < match_created[0]:
                                try:
                                    fw.delete_acquisition(match_ids[0])
                                    # out_list.append([match_labels[0], match_labels[1], \
                                                     # match_created[0], match_created[1]])
                                except:
                                    continue
        print(f'DONE: {sub.label} / {ses.label}')


out_df = pd.DataFrame(out_list, columns=['acq1','acq2','cond1','cond2'])
out_df.to_csv('acqs_to_delete.csv',index=False)



        # for label in acq_labels:
            # this_label = label.replace(' ','_')
            # indices = [i for i, x in enumerate(acq_labels) if fuzz.ratio(x.replace(' ','_'), this_label) >= 90]

