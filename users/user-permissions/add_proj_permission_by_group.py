# Add all users in a Flywheel group to a specific project
#   inherits group-level permissions based on template to project permission
#
#   assumes project belongs to group (can be modified if belongs to a different group)
#
#   amf July 2021
#
#       Example usage:
#           python3 path/to/add_proj_permission_by_group.py --key <your-api-key-here>
#                                                 --group <fw-group-label> --project <target-project>


import flywheel
import pandas as pd
import argparse

# ==========================================================================================

def is_group_valid(group_id):
    """Check if group id is valid"""
    try:
        fw_group = fw.get_group(group_id)
        return fw_group
    except:
        print(f'Invalid group-{group_id}')
        # log.error(f'Invalid group-{group_id}')
        return None

def find_and_get_project(grp_id, proj_label):
    """Find and get project container in the specified group"""
    group_container = is_group_valid(grp_id)

    if group_container:
        try:
            project_container = group_container.projects.find_one(f'label={proj_label}')
            return project_container
        except Exception as e:
            print(f'*Multiple project with the same label found. Unable to get the project container. Details {e}*')
            # log.error(f'*Multiple project with the same label found. Unable to get the project container. Details {e}*')
            return None

def apply_group_template_to_project(user_id, project, grp_id):
    """Update all user permission within a group across all project"""
    # Group permissions template
    group_container = fw.get_group(grp_id)
    permissions = group_container.permissions_template # permissions to copy

    users = [x.id for x in project.permissions]

    modified_msg = False

    for permission in permissions:
        if not isinstance(
                permission, flywheel.models.roles_role_assignment.RolesRoleAssignment
        ):
            permission = flywheel.RolesRoleAssignment(
                permission["id"], permission["role_ids"]
            )

        if permission.id not in users and user_id == permission.id:
            print(f'\tAdding {permission.id} into Project {project.label}')
            # log.info(f'\tAdding {permission.id} into Project {project.label}')
            try:
                project.add_permission(permission)
                print(f'\t\tSuccesfully added {user_id} to the Project permission ')
                # log.info(f'\t\tSuccesfully added {user_id} to the Project permission ')

            except Exception as e:
                print(f'*Error in adding {user_id} to the Project {project.label}. Details: {e}*')
                # log.error(f'*Error in adding {user_id} to the Project {project.label}. Details: {e}*')
            else:
                modified_msg = True

    if not modified_msg:
        print(f'*{user_id} did not have permission in the group, so will not be added to {project.label}*')
        # log.warning(
            # f'*{user_id} did not have permission in the group, so will not be added to {project.label}*')


# ==========================================================================================

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='This is a program to add all users in a group '
                                                 'to a project.'
                                                 '\nThis program is designed for Site Admin user only. It '
                                                 'required API Key, group name, & project name as input.\n'
                                                 'Example Code:\n\t'
                                                 'python path/to/add_proj_permission_by_group.py --key <your-api-key-here> '
                                                 '--group <fw-group-label> --project <target-project>')
    parser.add_argument('--key', dest='api_key', metavar='Key', help='API Key')
    parser.add_argument('--group', dest='group_name', required=True, help='Group name')
    parser.add_argument('--project', dest='proj_label', required=True, help='Project name')

    args = parser.parse_args()

    api_key=args.api_key
    group_name=args.group_name
    proj_label=args.proj_label

    fw = flywheel.Client(api_key)

    ## grab users for a group
    group = fw.get_group(group_name)
    proj_container = find_and_get_project(group_name.strip().lower(), proj_label.strip())

    ## add each user in the group to the target project
    ## using their group-level permission status
    for usr in group.permissions:
        user_email = usr.id
        apply_group_template_to_project(user_email, proj_container, group_name)

