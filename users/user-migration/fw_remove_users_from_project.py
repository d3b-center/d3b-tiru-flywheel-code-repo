## Removes all users (except those denoted to keep) from original project
#
#   where target projects end in "_v2" and original have the same name (minus "_v2")

import flywheel

fw = flywheel.Client()

target_group = 'd3b_archive'
users_to_retain = ['ariana@d3b.center']
string_to_match = 'ZZZ_'

print(f'Finding all projects in group {target_group}')
all_projects = fw.projects()
fw_group = fw.get_group(target_group)

for proj in all_projects:
    if string_to_match in proj.label:
        # print(proj.label)
        existing_users = [x.id for x in proj.permissions] # users already in target proj
        orig_proj_label = proj.label
        # orig_proj_label = proj.label.split('_v2')[0]
        try:
            orig_proj = fw_group.projects.find_one(f'label={orig_proj_label}') # retrieve orig project container
            print(f'Processing project {orig_proj_label}')
        except:
            orig_proj = []
            print(f'PROJECT {orig_proj_label} NOT FOUND. Skipping...')
        if orig_proj:
            orig_proj_permissions = orig_proj.permissions
            for user in orig_proj_permissions: # for each user in the original project
                if user.id not in users_to_retain:
                    fw.delete_project_user_permission(orig_proj.id, user.id)
                    print(f'\tRemoved {user.id} from Project {orig_proj.label}')
