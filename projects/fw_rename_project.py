## Rename original project labels
#
#   where target projects end in "_v2" and original have the same name (minus "_v2")

import flywheel

fw = flywheel.Client()

target_group = 'd3b'
users_to_retain = ['ariana@d3b.center']

print(f'Finding all projects in group {target_group}')
all_projects = fw.projects()
fw_group = fw.get_group(target_group)

for proj in all_projects:
    if '_v2' in proj.label:
        # print(proj.label)
        orig_proj_label = proj.label.split('_v2')[0]
        try:
            orig_proj = fw_group.projects.find_one(f'label={orig_proj_label}') # retrieve orig project container
            print(f'Processing project {orig_proj_label}')
        except:
            orig_proj = []
            print(f'PROJECT {orig_proj_label} NOT FOUND. Skipping...')
        if orig_proj:
            target_proj_label = 'ZZZ_'+orig_proj.label
            body = flywheel.models.Project(label = target_proj_label)
            fw.modify_project(orig_proj.id, body)
            print(f'Project label >> {orig_proj_label} << changed to >> {target_proj_label} <<')
