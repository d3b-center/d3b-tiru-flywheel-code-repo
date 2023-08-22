import shutil

import flywheel
import os
import re
from pathlib import Path
import pathvalidate as pv


proj_name = 'Sample-Test'
# =================================================================
fw = flywheel.Client('')
project = fw.projects.find_first(f'label={proj_name}')
output_path ='Acq/'

# Loop over all sessions
for ses in project.sessions.iter():
    ses_label = ses.label
    sub_label = ses.subject.label
    acq= ses.acquisitions
    print(sub_label)
    print(ses_label)
    for acq in ses.acquisitions.iter():
        acq_label=acq.label
        acq_id =acq.id
        for file_obj in acq.files:
            fname = file_obj.name
            t1=re.search('Path.*',fname) # specify the filename if you wanted to download a particular file
            print(fname)
            if t1:
                print(fname)
                this_path = os.path.join(output_path, sub_label, ses_label, acq_label)
                if not os.path.exists(this_path):
                    os.makedirs(this_path)
                    fw.download_file_from_acquisition(acq_id, fname,fname)
                    shutil.move(fname, this_path)



