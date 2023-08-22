# This script runs the File classifier gear on niftis
#   for any acquisition in a project containing a JSON sidecar
#       amf
#       Sept 2021


# flywheel_proj = 'LGG'
# 'HGG','Medullo','ATRT','DNET','Ependymoma','DIPG'
# fw_projects=['Corsica']
fw_projects=['Ependymoma','DIPG']

import flywheel
from datetime import datetime

## Access the flywheel client for your instance
fw = flywheel.Client('chop.flywheel.io:7NDu1QVmIawEWQvczj') # d3b dev

## Load project
# 

## Load gear
the_gear = fw.lookup('gears/file-classifier')

## Initialize gear job list
job_list = list()

# for project in fw.projects.iter():
for project_name in fw_projects:
    project = fw.projects.find_one('label='+project_name)
    proj_label = project.label
    if proj_label not in ['Sample','CBTN_D0143','CBTN_D0146']:
        print('Processing project '+proj_label)
        for session in project.sessions.iter():
            has_json = 0
            nii_file = {}
            inputs = {'file-input':[]}
            for acq in session.acquisitions():
                # print(acq.label)
                for file in acq.files:
                     # if nii file w/o classification
                    if (file['type'] == 'nifti') and (file.classification=={}) \
                        and (file['modality']!='CT') \
                        and (file['modality']!='PT') \
                        and ('localizer' not in file['name'].lower()) \
                        and ('scout' not in file['name'].lower()) \
                        and ('3_plane' not in file['name'].lower()) \
                        and ('three_plane' not in file['name'].lower()) \
                        and ('3plane' not in file['name'].lower()):
                    try:
                        if file.classification['Intent']:
                            has_class=1
                        else:
                            has_class=0
                    except:
                        has_class=0
                    # if (file['type'] == 'nifti') and (has_class==0) and ('_mpr' in file['name'].lower()):
                        nii_file = file
                        inputs['file-input'] = nii_file
                        dest = nii_file.parent # The destination for this anlysis will be on the acquisition
                        # time_fmt = '%d-%m-%Y_%H-%M-%S'
                        # analysis_label = f'File-classifier-{}'
                        job_id = the_gear.run(inputs=inputs, \
                                                destination=dest )
                        job_list.append(job_id)
                        print('Running File classifier on '+proj_label+' '+acq.label)



# loop through all acquisitions in each session of the project
# if the session contains a JSON, run the classifier gear on it
# for session in project.sessions.iter():
#     has_json = 0
#     nii_file = {}
#     inputs = {'file-input':[]}
#     for acq in session.acquisitions():
#         # print(acq.label)
#         for file in acq.files:
#             if file.name[-4:] == 'json': # type = 'source code'
#                 has_json = 1
#             elif file['type'] == 'nifti':
#                 nii_file = file
#         if has_json:
#             inputs['file-input'] = nii_file
#             dest = nii_file.parent # The destination for this anlysis will be on the acquisition
#             # time_fmt = '%d-%m-%Y_%H-%M-%S'
#             # analysis_label = f'File-classifier-{}'
#             job_id = the_gear.run(inputs=inputs, \
#                                     destination=dest )
#             job_list.append(job_id)
#             print('Running File classifier on '+acq.label)
