# define a list of files using Flywheel's DataView functionality
#   then loop through files & download them to current working dir
# 
#       assumes user has appropriate project permissions
#
# Dataview info: https://flywheel-io.gitlab.io/product/backend/sdk/branches/master/python/getting_started_new.html#id6

import flywheel
import os

# ========= user input ====================
api_key='<insert-API-key-here>' # Flywheel API key

fw_proj_label = 'LGG_PBTA_diffusion' # project to download data from
output_dir = 'data' # name of local dir to download data to

# ========= connect to Flywheel ====================
fw = flywheel.Client(api_key) # if already logged in via CLI, can use instead: fw = flywheel.Client()

# ========= get file info for entire project ====================
# define a DataView to get file info
#   can change "filename" string match to only include certain file types (e.g., *.nii.gz)
#   can include any Flywheel metadata fields as a column
view = fw.View(
    container="acquisition",
    filename="*",
    match="all",
    columns=[
        "file.name",
        "file.modality",
        "file.classification.Intent",
        "file.classification.Features",
        "file.classification.Measurement",
    ],
    include_ids=True,
    include_labels=True,
    process_files=False,
    sort=False,
)

# get the DataView for this project as a dataframe
project_info = fw.projects.find_first(f'label={fw_proj_label}')
project_df = fw.read_view_dataframe(view, project_info.id)

# ========= select certain files to download based on criteria ====================
# filter results to files of-interest
# project_df = project_df[project_df['acquisition.label'].str.contains('Files')] # filter to only acquisitions labelled "Files"
files_to_download = project_df[project_df['file.name'].str.contains('t1')] # only files containing "t1" in file name
# files_to_download = project_df[project_df['file.name'].str.contains('t1') & ~project_df['file.name'].str.contains('t1ce')] # don't include "t1ce"
# files_to_download = project_df[project_df['file.name'] == 'WT_segmentation_combined_mask.nii.gz'] # only files with this specific name
# files_to_download = project_df[(project_df['subject.label']=='C111930') & (project_df['acquisition.label'].str.contains('ADC'))] # specific subject and acquisition

## ***** example to only include/exclude certain subjects as listed in a CSV:
# import pandas as pd
# sub_df = pd.read_csv('sub_list.csv')
# sub_list = sub_df[['C_id']].drop_duplicates().tolist() # where "C_id" is the column header
# files_to_download = project_df[project_df['subject.label'].isin(sub_list)] # to exclude subjects in the list can change to: project_df[~project_df['subject.label'].isin(sub_list)]

## ***** example to only include certain subjects & sessions (based on age-in-days) as listed in a CSV:
# import pandas as pd
# sub_df = pd.read_csv('sub_list.csv')
# sub_df['cid_age'] = sub_df['C_id'].astype(str) + '_' + df['age_in_days'].astype(str)
# sub_list = sub_df[['cid_age']].drop_duplicates().tolist()
# project_df['age'] = project_df['session.label'].str.split('d_', 1, expand=True)[0]
# project_df['cid_age'] = sub_df['subject.label'].astype(str) + '_' + df['age'].astype(str)
# files_to_download = project_df[project_df['cid_age'].isin(sub_list)]

# ========= download selected files ====================
for ind,row in files_to_download.iterrows():
    sub_label = row['subject.label']
    ses_label = row['session.label']
    file_name = row['file.name']
    acq_id = row['acquisition.id']
    acquisition = fw.get(acq_id)
    output_path = os.path.join(output_dir, sub_label, ses_label) # path where you want the files to save locally
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    acquisition.download_file(file_name, os.path.join(output_path,file_name))
