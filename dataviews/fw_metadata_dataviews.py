"""
Fetch acquisition files linked to project/subject/session labels from Flywheel
"""
import os
import re
import json
import flywheel
import pandas as pd
from yaspin import yaspin

fw_api_token = os.getenv("FW_DEV_API_KEY")
assert fw_api_token
cbtn_all = pd.read_csv(os.getenv('cbtn_all_table'))
cbtn_all = cbtn_all[['CBTN Subject ID','Organization Name']].drop_duplicates()
fw = flywheel.Client(fw_api_token)

# Get file metadata quickly with Views. This is relatively fast.
view = fw.View(
    container="subject",
    match='all',
    include_ids=False,
    include_labels=True,
    process_files=False,
    sort=False,
)

# Get dataviews for all projects w/access
all_data = []
for project in fw.projects.iter():
    pid = project.id
    proj_name = project.label
    grp = project.group
    if ((grp == 'd3b') & ('_v2' in proj_name) & ('Adenoma' in proj_name)):
        with yaspin(text=f"Fetching view for project {proj_name} ({pid})...") as spin:
            d = json.load(fw.read_view_data(view, pid, decode=False, format="json-flat"))
            all_data.extend(d)
            spin.text = f"Found {len(d)} results for project {proj_name} ({pid})."
            spin.ok("✅")

# df = fw.read_view_dataframe(view, pid)

# Save file records.
if all_data:
    rex = re.compile(r"(?<!_)(?=[A-Z])")
    df = (
        pd.DataFrame(all_data)
        .rename(columns=lambda x: x.replace(".", "_"))  # avoid "." in colnames
        .rename(columns=lambda x: rex.sub("_", x).lower())  # camelcase to snake
    )
    df = df.merge(cbtn_all,how='left',left_on='subject.label',right_on='CBTN Subject ID')
    df.to_csv('fw_file_meta.csv',index=False)
else:
    print("No files found.")
