"""
This script applies a gear rule to all projects in the d3b group 
with '_v2' in the project label. The gear rule is configured to 
trigger the 'import nifti sidecar metadata' gear when a file of 
type 'nifti' is added to the project. The gear will be run with 
the specified role and will not auto-update or be disabled.
"""

import os
import flywheel

# Configuration
print('Initializing Flywheel client...')
FLYWHEEL_API_KEY = os.getenv('FW_API_KEY')
fw = flywheel.Client(FLYWHEEL_API_KEY)

print('Applying gear rules to projects...')
for project in fw.projects.iter(limit=5):
    if ('_v2' in project.label) and (project.parents.group == 'd3b'):
        print(f'Project: {project.label}, ID: {project.id}')
        condition_body = flywheel.models.GearRuleCondition(type='file.type', value='nifti', regex=None)
        body = flywheel.models.GearRuleInput(project_id=project.id, 
                                                gear_id='699f8adc0c29a15f4e83eff8', 
                                                role_id='5eea7eb40111dd000fe3dd36', 
                                                name='import nifti sidecar metadata', 
                                                config=None, 
                                                fixed_inputs=None, 
                                                priority=None, 
                                                auto_update=False, 
                                                any=[condition_body],
                                                all=None,
                                                _not=None, 
                                                disabled=False, 
                                                compute_provider_id=None, 
                                                triggering_input=None)
        fw.add_project_rule(project.id, body)
    else:
        print(f'Skipping project: {project.label}, ID: {project.id}')