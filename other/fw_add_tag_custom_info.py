import flywheel
import os

fw = flywheel.Client(os.getenv('FW_API_KEY'))

proj_tags = {'Pediatric_auto_deface':'training',\
             'Pediatric_auto_deface_internal_test':'testing-internal',\
             'Pediatric_auto_deface_external_test':'testing-external',\
             'Pediatric_auto_deface_external_test_SLIPcohort':'testing-slip',\
            }

for project_name,tag in proj_tags.items():
    proj_container = fw.projects.find_first(f'label={project_name}')
    proj_container = proj_container.reload()
    print(f'******************* {proj_container} ***********************')
    for session in proj_container.sessions.iter():
        session.add_tag(tag)
        session.update_info({ 'study_cohort': tag })
        print(f'DONE: {session.subject.label}/{session.label}')
