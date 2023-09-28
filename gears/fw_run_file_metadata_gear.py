## run a utility gear via SDK

import flywheel

fw = flywheel.Client()

# ========================  User defined inputs =========================================
# define Flywheel project to run the gear within

# proj_name = 'CBTN_histology_proc'
# project = fw.projects.find_first(f'label={proj_name}')

project = fw.get_project('60f6fdfa96ec5075ccbf344a') # 'Ambra_raw_external_data'

# define the gear name (needs to match that in Flywheel config file)
gear_name = 'file-metadata-importer'

# ========================= Main processes ========================================

## Initialize gear stuff
gear2run = fw.lookup(f'gears/{gear_name}')
job_list = list()

# Loop over all sessions in the project
for ses in project.sessions.iter():
    # initialize gear stuff
    inputs = {'input-file':[]}
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
            fname = file_obj.name
            # if there is no file metadata, run the gear
            if (file_obj.info=={}):
                inputs['input-file'] = file_obj
                job_id = gear2run.run(inputs=inputs) # config={'Subject':subject.label}
                job_list.append(job_id)
                print(f'Queued: {sub_label}/{ses_label} - {fname}')
