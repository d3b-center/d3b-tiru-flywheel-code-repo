import flywheel

fw = flywheel.Client() # assumes logged in via command-line

project_label = 'BraTS_DIPGr'

# ====== set up data view ==========
view = fw.View(
    container="acquisition",
    match="all",
    columns=[
        "acquisition.label",
    ],
    include_ids=True,
    include_labels=True,
    process_files=False,
    sort=False,
)

project = fw.projects.find_first(f'label={project_label}');

# get dataframe for all SVS files on Flywheel using DataView tool
flywheel_df = fw.read_view_dataframe(view, project.id) # dataframe with all files in this proj

# select the "bad" acquisitions that we want to delete
#       in this case, this is all of the acquisitions with "Screen Save" in their label
flywheel_df['acquisition.label_lower'] = flywheel_df['acquisition.label'].str.lower()
bad_acqs = flywheel_df[flywheel_df['acquisition.label_lower'].str.contains('screen')]

# now delete those selected acquisitions
for ind,row in bad_acqs.iterrows():
    acq_id = row['acquisition.id']
    fw.delete_acquisition(acq_id)
