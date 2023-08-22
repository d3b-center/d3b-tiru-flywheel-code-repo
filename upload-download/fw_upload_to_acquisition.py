
# expects local data structure:
#       local_data_dir / subject_ses / *.nii.gz
import flywheel
import os
import shutil
from glob import glob
import json

api_key = '' # YOUR API KEY
fw = flywheel.Client(api_key)

fw_proj_name = 'LGG-feature-extraction' # name of the Flywheel project to upload to

local_data_dir = '' # directory that contains the data files

# ==============================================================================
proj_cntr = fw.projects.find_first(f'label={fw_proj_name}')

for adc_file_path in glob(local_data_dir+'/*/*_adc_*'): # for each file in the data_dir with _adc_ in the file name
    adc_file_name = os.path.basename(adc_file_path) # get just the file name
    c_id = adc_file_name.split('_')[0] # c-id is the first part of the file name
    session = adc_file_name.split('_')[1] # session is the second part of the file name
    # get the destination acquisition container
    acq_cntr = fw.lookup(f'{proj_cntr.group}/{proj_cntr.label}/{c_id}/{session}/Acquisitions') # can use lookup with the Flywheel hierarchy path
    # upload the local file to the acquisition
    acq_cntr.upload_file(adc_file_name)
