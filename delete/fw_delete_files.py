# remove incorrect file names, e.g., "_-_" "__"
# check for duplicate slide numbers in manifest that may have been processed incorrectly

# QC for pathology manifest
    # clean SDG-IDs

import flywheel


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

## =============== DONE ===============

# with_commas = flywheel_df[flywheel_df['file.name'].str.contains(',')]
# for ind,row in with_commas.iterrows():
#     fw.delete_acquisition_file(row['acquisition.id'], row['file.name'])

# with_dash = flywheel_df[flywheel_df['file.name'].str.contains('_-_')]
# for ind,row in with_dash.iterrows():
#     fw.delete_acquisition_file(row['acquisition.id'], row['file.name'])
