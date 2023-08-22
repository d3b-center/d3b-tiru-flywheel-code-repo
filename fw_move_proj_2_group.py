## Move project to a different Flywheel group
#

import flywheel

fw = flywheel.Client()

source_group = 'd3b'
target_group = 'tiru'
project_name = 'Arastoo_IRB_protocol'

print(f'Finding project {project_name} in group {source_group}')
proj_container = fw.projects.find_first('label='+project_name)

print(f'Changing project to group {target_group}')
body = flywheel.models.Project(group = target_group)
fw.modify_project(proj_container.id, body)
