# get a list of all files in the project
#   find subjects missing any of the 4 base scans
#   find subjects with duplicate files (?)

import flywheel

fw = flywheel.Client()

project_name = 'CBTN_processed_segmentations_Box'
project = fw.lookup(f'tiru/{project_name}')
project_id = project.id

view = fw.View(
    container="acquisition",
    filename="*.nii.gz",
    match="all",
    columns=[
        "file.name",
    ],
    include_ids=False,
    include_labels=True,
    process_files=False,
    sort=False,
)

# get dataframe of all files in the project
df = fw.read_view_dataframe(view, project_id)

df.to_csv('Flywheel_file_list.csv', index=False)

# check for all 4 base scans within each subject
sub_list = df['subject.label'].drop_duplicates().tolist()
for sub_id in sub_list:
    ses_label = df[df['subject.label']==sub_id]['session.label'].tolist()[0]
    sub_file_list = df[df['subject.label']==sub_id]['file.name'].tolist()
    t1ce = f'{sub_id}_{ses_label}_T1CE_to_SRI.nii.gz'
    t1 = f'{sub_id}_{ses_label}_T1_to_SRI.nii.gz'
    t2 = f'{sub_id}_{ses_label}_T2_to_SRI.nii.gz'
    fl = f'{sub_id}_{ses_label}_FL_to_SRI.nii.gz'
    if t1ce not in sub_file_list:
        print(f'SUBJECT {sub_id} missing T1CE')
    if t1 not in sub_file_list:
        print(f'SUBJECT {sub_id} missing T1')
    if t2 not in sub_file_list:
        print(f'SUBJECT {sub_id} missing T2')
    if fl not in sub_file_list:
        print(f'SUBJECT {sub_id} missing FLAIR')

# check for Segmentation file for each subject
sub_list = df['subject.label'].drop_duplicates().tolist()
for sub_id in sub_list:
    ses_label = df[df['subject.label']==sub_id]['session.label'].tolist()[0]
    sub_file_list = df[df['subject.label']==sub_id]['file.name'].tolist()
    seg_file = f'{sub_id}_{ses_label}_ManualSegmentation.nii.gz'
    if seg_file not in sub_file_list:
        print(f'SUBJECT {sub_id} missing ManualSegmentation')

