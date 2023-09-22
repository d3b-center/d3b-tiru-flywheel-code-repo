## run a utility gear via SDK

import flywheel
from datetime import datetime
import os

fw = flywheel.Client()

# ========================  User defined inputs =========================================
# define Flywheel project to run the gear within
proj_name = 'CBTN_histology_proc'

# define the gear name (needs to match that in Flywheel config file)
gear_name = 'openslide-to-png'

# ========================= Main processes ========================================
project = fw.projects.find_first(f'label={proj_name}')

## Initialize gear stuff
gear2run = fw.lookup(f'gears/{gear_name}')
job_list = list()

# Loop over all sessions in the project
for ses in project.sessions.iter():
    # initialize gear stuff
    inputs = {'image':[]}
    # get info
    ses_label = ses.label
    sub_label = ses.subject.label
    # Make sure we have all our analysis since we got the session through an iterator, and not "fw.get()'
    ses = ses.reload()
    # loop through the acquisitions in the session
    for acq in ses.acquisitions.iter():
        # build a list of all file names in the current acquisition
        acq_file_list=[]
        for file_obj in acq.files:
            acq_file_list.append(file_obj.name)
        # now queue the gear for any SVS file without an associated PNG in the same acquisition
        for file_obj in acq.files:
            fname = file_obj.name
            if ('*.png' not in fname) and \
                (os.path.splitext(fname)[0]+'.png' not in acq_file_list):
                inputs['image'] = file_obj
                job_id = gear2run.run(inputs=inputs) # config={'Subject':subject.label}
                job_list.append(job_id)
                print(f'Queued: {sub_label}/{ses_label} - {fname}')
