# Delete files on Flywheel
#   amf
#   Sept 2021
#
#   for a given project, deletes any DICOM files
#   uses data-view to select DICOM files
#
# 
# example usage:
#       python3 fw_delete_DICOMs.py [fw-project]

# ====== user input ====== 
# fw_proj='CBTN_D0143'
# api_key='chop.flywheel.io:l60oYWEMahamvtTl7k'


import flywheel
import csv
import os
import sys

if len(sys.argv) < 2:
    print('ERROR: Not enough input arguments (usage: python3 fw_deid_export.py [fw-proj])')
    sys.exit()
else:
    fw_proj = sys.argv[1]

# ====== access the flywheel client for the instance ====== 
fw = flywheel.Client()

# ====== set up data view ==========
view = fw.View(
    container="acquisition",
    filename="*",
    match="all",
    columns=[
        "file.name",
        "file.file_id",
        "file.type",
        "file.info",
        "file.info.SeriesNumber",
    ],
    include_ids=True,
    include_labels=True,
    process_files=False,
    sort=False,
)

# ====== loop through subjects ====== 
project = fw.projects.find_first('label='+fw_proj)
df = fw.read_view_dataframe(view, project.id)

df_dicoms = df[df['file.type']=='dicom']

if df_dicoms.empty:
    print('No DICOMs found in '+fw_proj)
else:
    for ind,row in df_dicoms.iterrows():
        fw.delete_acquisition_file(row['acquisition.id'],row['file.name'])
        print(sub['label']+' file '+file['name']+' deleted on Flywheel')

# ====== delete empty acquisition containers ====== 
for sub in project.subjects():
    for ses in sub.sessions():
        for acq in ses.acquisitions():
            if not acq.files:
                fw.delete_acquisition(acq.id)
                print(sub['label']+' file '+acq['label']+' empty acquisition deleted on Flywheel')

                