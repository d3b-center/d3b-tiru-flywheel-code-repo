# Delete empty containers on Flywheel instance
#   amf
#   Sept 2021
#
#   for a given project, deletes empty acquisitions, then empty sessions, then empty subjects
#
#  
# example usage:
#       python3 fw_delete_empty_containers.py [fw-project]

# ====== user input ====== 

# fw_proj = 'CBTN_D0143_staging'


import flywheel
import sys

if len(sys.argv) < 2:
    print('ERROR: Not enough input arguments (usage: python3 fw_deid_export.py [fw-proj])')
    sys.exit()
else:
    fw_proj = sys.argv[1]

if fw_proj == 'CBTTC_V2':
    fw_group = 'cbttc'
else:
    fw_group = 'd3b'

fw_projects = ['HGG']

# ====== access the flywheel client for the instance ====== 
# fw = flywheel.Client(api_key)
fw = flywheel.Client()

# ====== loop through projects ====== 
grp_cntnr = fw.lookup(fw_group)
all_projects = grp_cntnr.projects()

# ====== delete empty acquisition containers ====== 
for proj in all_projects:
    if proj['label'] == fw_proj:
        print('Processing acquisitions: PROJECT '+proj['label'])
        for sub in proj.subjects():
            for ses in sub.sessions():
                for acq in ses.acquisitions():
                    if not acq.files:
                        fw.delete_acquisition(acq.id)
                        print('Deleted empty acquisition: PROJECT '+proj['label'] +' / SUBJECT '+ sub['label']+' / '+acq['label'])

# ====== delete empty session containers ====== 
for proj in all_projects:
    if proj['label'] == fw_proj:
        print('Processing sessions: PROJECT '+proj['label'])
        for sub in proj.subjects():
            for ses in sub.sessions():
                # ses = ses.reload()
                if len(ses.acquisitions()) == 0:
                    fw.delete_session(ses.id)
                    print('Deleted empty session: PROJECT '+proj['label'] +' / SUBJECT '+ sub['label']+' / SESSION '+ses['label'])


# ====== delete empty subject containers ====== 
for proj in all_projects:
    if proj['label'] == fw_proj:
        print('Processing subjects: PROJECT '+proj['label'])
        for sub in proj.subjects():
            if not sub.sessions(): # if sub doesn't have any sessions
                fw.delete_subject(sub.id)
                print('Deleted empty subject: PROJECT '+proj['label'] +' / SUBJECT '+ sub['label'])

