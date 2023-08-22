## Loops through all projects in a group
#   adds all users from "original" project to "target" project
#
#   where target projects end in "_v2" and original have the same name (minus "_v2")

import flywheel

fw = flywheel.Client()

target_group = 'd3b'

print(f'Finding all projects in group {target_group}')
all_projects = fw.projects()
fw_group = fw.get_group(target_group)

for proj in all_projects:
    if '_v2' in proj.label:
        # print(proj.label)
        existing_users = [x.id for x in proj.permissions] # users already in target proj
        orig_proj_label = proj.label.split('_v2')[0]
        try:
            orig_proj = fw_group.projects.find_one(f'label={orig_proj_label}') # retrieve orig project container
            print(f'Processing project {orig_proj_label}')
        except:
            orig_proj = []
            print(f'PROJECT {orig_proj_label} NOT FOUND. Skipping...')
        if orig_proj:
            orig_proj_permissions = orig_proj.permissions
            for user in orig_proj_permissions: # for each user in the original project
                if (user.id not in existing_users): # skip users already in the target project
                    if not isinstance(
                        user, flywheel.models.roles_role_assignment.RolesRoleAssignment ):
                        usr_permission = flywheel.RolesRoleAssignment(
                            user.id, user.role_ids )
                    print(f'\tAdding {usr_permission.id} into Project {proj.label}')
                    try:
                        proj.add_permission(usr_permission) # add the user to the target project
                        print(f'\t\tSuccesfully added {user.id} to the Project permission ')
                    except Exception as e:
                        print(f'*Error in adding {user.id} to the Project {proj.label}. Details: {e}*')
                    else:
                        modified_msg = True
