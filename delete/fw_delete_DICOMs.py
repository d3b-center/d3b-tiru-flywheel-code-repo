# Delete files on Flywheel
#   amf
#   Sept 2021, updated Oct 2025
#
#   for a given project, deletes any DICOM files
#   uses data-view to select DICOM files
#
# 
# example usage:
#       python3 fw_delete_DICOMs.py [fw-project]

import flywheel
import csv
import os
import sys

# ====== user input ====== 
# if len(sys.argv) < 2:
#     print('ERROR: Not enough input arguments (usage: python3 fw_deid_export.py [fw-proj])')
#     sys.exit()
# else:
#     fw_proj = sys.argv[1]

fw_proj = 'Adenoma_v2_copy'

# ====== access the flywheel client for the instance ====== 
fw = flywheel.Client(os.getenv('FW_API_KEY'))

# ====== set up data view ==========
view = fw.View(
    container="acquisition",
    filename="*",
    match="all",
    columns=[
        "file.name",
        "file.file_id",
        "file.type",
    ],
    include_ids=True,
    include_labels=True,
    process_files=False,
    sort=False,
)

# ====== loop through subjects ====== 
project = fw.projects.find_first(f'label={fw_proj}')
df = fw.read_view_dataframe(view, project.id)

df_dicoms = df[df['file.type']=='dicom']

if df_dicoms.empty:
    print('No DICOMs found in '+fw_proj)
else:
    n_files = len(df_dicoms)
    for ind,row in df_dicoms.iterrows():
        sub = row['subject.label']
        ses = row['session.label']
        file_name = row['file.name']
        fw.delete_acquisition_file(row['acquisition.id'],file_name)
        print(f'{ind+1}/{n_files} {sub}/{ses} file {file_name} deleted on Flywheel')

# ====== delete empty acquisition containers ====== 
for sub in project.subjects():
    for ses in sub.sessions():
        for acq in ses.acquisitions():
            if not acq.files:
                fw.delete_acquisition(acq.id)
                print(f'{sub.label}/{ses.label} file {acq.label} empty acquisition deleted on Flywheel')
