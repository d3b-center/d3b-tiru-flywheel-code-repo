# This script deletes classifications for all files in a project
#       amf
#       Jan 2022


flywheel_proj = 'Craniopharyngioma'

import flywheel
from datetime import datetime

## Access the flywheel client for your instance
fw = flywheel.Client()

## Load project
project = fw.projects.find_one('label='+flywheel_proj)

# loop through all acquisitions in each session of the project
# if the session contains a JSON, run the classifier gear on it
for session in project.sessions.iter():
    for acq in session.acquisitions():
        for file in acq.files:
            file = fw.get_file(file.file_id)
            acq.replace_file_classification(file.name,{}) # this one works
            print('Removed classification: '+acq.label+' '+file.name)
