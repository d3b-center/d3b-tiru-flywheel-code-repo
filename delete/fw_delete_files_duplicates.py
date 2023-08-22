# remove incorrect file names, e.g., "_-_" "__"
# check for duplicate slide numbers in manifest that may have been processed incorrectly

# QC for pathology manifest
    # clean SDG-IDs

import flywheel
import pandas as pd

fw = flywheel.Client() # d3b dev

# ====== set up data view ==========
view = fw.View(
    container="acquisition",
    filename="*svs*",
    match="all",
    columns=[
        "file.name",
    ],
    include_ids=True,
    include_labels=True,
    process_files=False,
    sort=False,
)

project_label = 'CBTN_histology'
project = fw.projects.find_first(f'label={project_label}');

# get dataframe for all SVS files on Flywheel using DataView tool
flywheel_df = fw.read_view_dataframe(view, project.id) # dataframe with all files in this proj
flywheel_df = flywheel_df[~flywheel_df['file.name'].isnull()] # remove NaNs
flywheel_df['file.name_short'] = flywheel_df['file.name'].apply(lambda x: x.split('.svs')[0]) # get the file names w/o file ending

# import list of files to delete from CSV
files_to_delete = pd.read_csv('Path-ETL/duplicate_slide_numbers.csv')
files_to_delete = files_to_delete[['SDG_ID', 'SLIDES_updated']]

files_to_delete_df = files_to_delete.merge(flywheel_df, left_on=['SDG_ID','SLIDES_updated'], right_on=['session.label','file.name_short'])

ind=1
n_files=len(files_to_delete_df)
for index,row in files_to_delete_df.iterrows():
    try:
        fw.delete_acquisition_file(row['acquisition.id'], row['file.name'])
        print(f'DELETED: {str(ind)}/{n_files}')
    except:
        print(f'NOT FOUND: {str(ind)}/{n_files}')        
    ind+=1

## =============== DONE ===============

# with_commas = flywheel_df[flywheel_df['file.name'].str.contains(',')]
# for ind,row in with_commas.iterrows():
#     fw.delete_acquisition_file(row['acquisition.id'], row['file.name'])

# with_dash = flywheel_df[flywheel_df['file.name'].str.contains('_-_')]
# for ind,row in with_dash.iterrows():
#     fw.delete_acquisition_file(row['acquisition.id'], row['file.name'])
