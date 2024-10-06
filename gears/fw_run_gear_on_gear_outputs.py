# Script that uses Flywheel SDK to loop through sessions in a
# Flywheel project, look for requisite files in the session and
# if the files are found then queue up the desired
# gear to run on the files.

# only runs for files with existing deepliif-predict analysis containers
# only runs if file does not already have a deepliif-compute analysis container

import flywheel
from datetime import datetime
time_fmt = '%m/%d/%Y %H:%M:%S'
import os

fw = flywheel.Client(os.getenv('FW_API_KEY'))

# define Flywheel project to run the gear within
proj_name = 'CBTN_ki-67'
gear_name = 'deepliif-compute-scores'

proj_cntr = fw.projects.find_first(f'label={proj_name}')

## Initialize gear stuff
gear2run = fw.lookup(f'gears/{gear_name}')
job_list = list()

count=0
for ses_cntr in proj_cntr.sessions.iter():
    if ses_cntr.label != 'Test':
        for acq in ses_cntr.acquisitions.iter():
            for file in acq.files:
                if ('ki' in file.name.lower()) & ('.png' not in file.name): # skip PNG images
                    # find deepliif-predict results
                    ses_cntr = ses_cntr.reload()
                    analyses = ses_cntr.analyses
                    matches = [asys for asys in analyses if asys.gear_info.get('name') == gear_name] # if this gear was not already run
                    matches = [match for match in matches if match.job.inputs['image']['name'] == file.name] # for this specific file
                    if len(matches) == 0:
                        # setup the output files from the DeepLIIF-predict gear job for this specific file
                        matches = [asys for asys in analyses if asys.gear_info.get('name') == 'deepliif-predict']
                        matches = [match for match in matches if match.job.state in ['failed','complete']]
                        matches = [match for match in matches if match.job.inputs['image']['name'] == file.name]
                        if len(matches) > 0:
                            match = matches[0]
                            # initialize gear stuff
                            inputs = {'image':[], 'refined-segmentation':[]}
                            # get the predicted segmentation image
                            for output_file in match.files:
                                if 'SegRefined' in output_file.name:
                                    inputs['refined-segmentation'] = output_file
                            if inputs['refined-segmentation'] != []:
                                analysis_label = f'{gear_name} {datetime.now().strftime(time_fmt)}'
                                inputs['image'] = file
                                for low_thresh in [5,25,50,100]:
                                    for up_thresh in [100,500,1000,5000]:
                                        job_id = gear2run.run(inputs=inputs, config={'marker_thresh':'auto','resolution':'None', 'seg_thresh':150, \
                                                                                    'size_thresh':f'{low_thresh}', 'size_thresh_upper':f'{up_thresh}'}, \
                                                                            destination=ses_cntr, \
                                                                            )
                                job_list.append(job_id)
                                count+=1
                                print(f'Queued {count}: {ses_cntr.subject.label}/{ses_cntr.label} - {file.name}')
