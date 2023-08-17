import flywheel
import re

fw = flywheel.Client('') # d3b dev
view = fw.View(
    container="session",
    match="all",
    filename="*",
    include_ids=True,
    include_labels=True,
    process_files=False,
    sort=False,
)

for project in fw.projects():
    if re.search('.*_v2',project.label):
        print(project.label)
        flywheel_df = fw.read_view_dataframe(view,project.id) # dataframe with all files in this proj
        flywheel_df = flywheel_df[['subject.label', 'session.label','project.label']]
        flywheel_df.to_csv('flywheel_all.csv',mode='a', index=False, header=False)
