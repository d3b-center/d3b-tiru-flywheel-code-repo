#  Add age_days to session metadata
#   amf
#   Aug 2024
#

import flywheel
import os
# import backoff
# from flywheel.rest import ApiException

fw_api_token = os.getenv("FLYWHEEL_API_TOKEN")

# ====== access the flywheel client for the instance ====== 
fw = flywheel.Client(fw_api_token) # d3b dev

# ====== loop through projects ======
for project in fw.projects.iter():
    proj_label = project.label
    if '_v2' in proj_label:
        print('PROCESSING: '+proj_label)
        project = project.reload() # project = fw.projects.find_first('label='+proj_label)
        for session in project.sessions.iter():
            session = session.reload()
            if not session.age_days: # if age not already assigned
                session_label = session.label
                age_in_days = int(session_label.split('d_')[0])
                age_in_secs = age_in_days * 24 * 60 * 60
                # age is stored in seconds on flywheel
                session.update({'age':age_in_secs})
                print(f'UPDATED: {session.subject.label}/{session.label} with age_days = {age_in_days}')
