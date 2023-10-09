# script to copy files from 1 project to another

import os
import flywheel

fw = flywheel.Client(os.getenv('FW_API_KEY'))

source_fw_proj = 'Pediatric_auto_deface'
source_proj_cntr = fw.projects.find_first('label='+source_fw_proj)

dest_fw_proj = 'Pediatric_auto_deface_ModelPredictions'
dest_proj_cntr = fw.projects.find_first('label='+dest_fw_proj)

for dest_ses in dest_proj_cntr.sessions.iter():
    # print(dest_ses)
    for acq in dest_ses.acquisitions.iter(): # can do this b/c we know there's only 1 acquisition
        dest_acq = acq
    source_sub_cntr = source_proj_cntr.subjects.find_first(f'label={dest_ses.subject.label}')
    for source_ses in source_sub_cntr.sessions.iter():
        for source_acq in source_ses.acquisitions.iter():
            for source_file in source_acq.files:
                # print(source_file.name)
                if source_file.name in ['t1.nii.gz','t1ce.nii.gz','flair.nii.gz','t2.nii.gz']: # only copy these 4 files
                    source_acq.download_file(source_file.name,source_file.name)
                    dest_acq.upload_file(source_file.name)
                    os.remove(source_file.name)
