## Move projects to a different Flywheel group
#
#   where target projects start with 'ZZZ_'

import flywheel

fw = flywheel.Client()

source_group = 'd3b'
target_group = 'd3b_archive'

print(f'Finding all projects in group {source_group}')
all_projects = fw.projects()
fw_group = fw.get_group(source_group)

for proj in all_projects:
    if ('ZZZ_' in proj.label):
        print(f'Processing project {proj.label}')
        body = flywheel.models.Project(group = target_group)
        try:
            fw.modify_project(proj.id, body)
        except:
            continue
