## Move project to a different Flywheel group
#

import flywheel
import os

fw = flywheel.Client(os.getenv('FW_API_KEY'))

source_group = 'd3b'
target_group = 'chordoma_foundation'
project_name = 'Chordoma_histology'

print(f'Finding project {project_name} in group {source_group}')
proj_container = fw.projects.find_first('label='+project_name)

print(f'Changing project to group {target_group}')
body = flywheel.models.Project(group = target_group)
fw.modify_project(proj_container.id, body)
