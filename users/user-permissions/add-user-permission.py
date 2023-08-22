#!/usr/env/bin python
# 'This is a program to find or create user and add the user '
#                                                  'to corresponding group & project.'
#                                                  '\nThis program is designed for Site Admin user only. It '
#                                                  'required API Key and CSV file as input.\n'
#                                                  'Example Code:\n\t'
#                                                  'python path/to/add-user-permission.py --key <your-api-key-here> '
#                                                  '--file path/to/user-permission-list.csv'

import flywheel
import logging
import argparse
import os
import pandas as pd
from pathlib import Path

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# CONSTANT
SITE_PERM_ORDER = ['user',
                   'developer',
                   'site_admin']

EMAIL_PREFIX = ''

PERMISSION_MAPPING = {
    'admin': 'admin',
    'read/write': 'rw',
    'read': 'ro'
}

PERMISSION_LABEL_MAPPING = {
    'admin': 'admin',
    'read/write': 'read-write',
    'read': 'read-only'
}

CSV_COLUMN_LIST = ['First Name',
                   'Last Name',
                   'EPPN',
                   'FW Group',
                   'Project Name',
                   'Site-Role',
                   'Project Permission']


def validate_file_type(f):
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError(f'{f} does not exist')
    if not f.endswith('.csv'):
        raise argparse.ArgumentTypeError(f'{f} is not in the right format.')
    else:
        df = pd.read_csv(f)
        df.drop(df.filter(regex="Unnamed"), axis=1, inplace=True)
        col_list = df.columns.tolist()
        if col_list != CSV_COLUMN_LIST:
            raise argparse.ArgumentTypeError(f'{f} needs to have the following {CSV_COLUMN_LIST} in the same order.')

    return f


def check_or_add_prefix(email):
    """Add prefix to the email"""
    if not email.endswith(EMAIL_PREFIX):
        return email + EMAIL_PREFIX
    else:
        return email


def find_or_add_user(index, firstname, lastname, email, site_role):
    """Find or create new user object with specified site role"""
    try:
        user_obj = fw.get_user(email)
    except flywheel.ApiException:
        log.info(f'{email} not found in the instance. Adding user...')
        if (site_role == 'nan') | (site_role not in SITE_PERM_ORDER):
            siterole = ['user']
        else:
            siterole = [site_role]

        if firstname and lastname and email and siterole:
            user_object = flywheel.User(id=email, email=email, firstname=firstname.title(),
                                        lastname=lastname.title(), roles=siterole)
            try:
                new_user = fw.add_user(user_object)

            except Exception as e:
                log.error(f'Error occured. Unable to add user {firstname}, {lastname}. Details: {e}')
                return None
            else:
                return new_user
        else:
            log.error(f'Missing information on the file. Unable to add user {index}')
            return None
    else:
        return user_obj


def is_group_valid(group_id):
    """Check if group id is valid"""
    try:
        fw_group = fw.get_group(group_id)
        return fw_group
    except:
        log.error(f'Invalid group-{group_id}')
        return None


def find_and_get_project(grp_id, proj_label):
    """Find and get project container in the specified group"""
    group_container = is_group_valid(grp_id)

    if group_container:
        try:
            project_container = group_container.projects.find_one(f'label={proj_label}')
            return project_container
        except Exception as e:
            log.error(f'*Multiple project with the same label found. Unable to get the project container. Details {e}*')
            return None


def find_project_roles_id(client, proj_permission):
    tmp_proj_permission = PERMISSION_LABEL_MAPPING[proj_permission]

    log.info(f'\tFinding role id for {proj_permission} in Instance')
    for i in client.get_all_roles():

        if i['label'] == tmp_proj_permission:
            role_list = [i['_id']]

    if role_list:
        return role_list
    else:
        log.error(f'*{tmp_proj_permission} is not found in the roles. Unable to add the user to the roles*')
        return None


def apply_group_template_to_project(user_id, project, grp_id):
    """Update all user permission within a group across all project"""
    # Group permissions template
    group_container = fw.get_group(grp_id)
    permissions = group_container.permissions_template

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
            log.info(f'\tAdding {permission.id} into Project {project.label}')
            try:
                project.add_permission(permission)
                log.info(f'\t\tSuccesfully added {user_id} to the Project permission ')

            except Exception as e:
                log.error(f'*Error in adding {user_id} to the Project {project.label}. Details: {e}*')
            else:
                modified_msg = True

    if not modified_msg:
        log.warning(
            f'*{user_id} did not have permission in the group, so will not be added to {project.label}*')


def add_user_to_grp_and_proj(fw, user_email, grp_id, proj_container, proj_permission):
    """Add user to group and update user permission across projects under the group container"""

    tmp_permission_label = PERMISSION_MAPPING[proj_permission]
    group_container = fw.get_group(grp_id)

    try:
        log.info(f'\tAdding {user_email} into group permission for {group_container.id} ')
        fw.add_group_permission(grp_id, {'_id': user_email, 'access': tmp_permission_label})
    except Exception as e:
        log.error(f'*Error in adding user to group {grp_id}. Details: {e}*')
    else:
        log.info(f'\t\tSuccessfully added {user_email} into group permission in {group_container.id} ')

    # Get the role id within the instance
    role_list = find_project_roles_id(fw, proj_permission)

    if role_list:
        try:
            log.info(f'\tAdding {user_email} into the Group permission template in {group_container.id}')
            # add user to the group template
            fw.add_group_permission_template(grp_id, {'_id': user_email, 'role_ids': role_list})
        except Exception as e:
            log.error(f'*Error in adding {user_email} to Group permission template in Group {grp_id}*')
        else:
            log.info(f'\t\tSuccessfully added user to the Group permission template in {group_container.id}')

            apply_group_template_to_project(user_email, proj_container, grp_id)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='This is a program to find or create user and add the user '
                                                 'to corresponding group & project.'
                                                 '\nThis program is designed for Site Admin user only. It '
                                                 'required API Key and CSV file as input.\n'
                                                 'Example Code:\n\t'
                                                 'python path/to/add-user-permission.py --key <your-api-key-here> '
                                                 '--file path/to/user-permission-list.csv')
    parser.add_argument('--key', dest='api_key', metavar='Key', help='API Key')
    parser.add_argument('--file', dest='input', required=True, type=validate_file_type, help='CSV File for adding '
                                                                                             'user to '
                                                                                             'instance',
                        metavar='CSV File')

    args = parser.parse_args()

    # fw = flywheel.Client(args.api_key)
    fw = flywheel.Client()

    user_roles = fw.get_current_user().roles

    if 'site_admin' in user_roles:

        df = pd.read_csv(Path(args.input)).dropna(how='all')

        for (index, firstname, lastname, email, grp_id, proj_label, site_role, proj_permission) in df.itertuples():
            log.info(f'\t\tLoading Row {index + 1}')
            # Make sure there is value in all column
            if not pd.isna(firstname) and not pd.isna(lastname) and not pd.isna(email) and not pd.isna(site_role) \
                    and not pd.isna(grp_id) and not pd.isna(proj_label) and not pd.isna(proj_permission):
                updated_email = check_or_add_prefix(email.strip())
                log.info(f'Finding or adding {updated_email} into the instance')

                user_obj = find_or_add_user(index, firstname.strip().title(), lastname.strip().title(), updated_email,
                                            site_role.lower())
                if user_obj:
                    # add user to the group and project template
                    log.info(f'Finding the {proj_label.strip()} Project container...')
                    project_container = find_and_get_project(grp_id.strip().lower(), proj_label.strip())
                    if project_container:
                        add_user_to_grp_and_proj(fw, updated_email, grp_id.strip().lower(), project_container,
                                                 proj_permission.strip().lower())
            else:
                log.error(f'Found empty value on {index} row. Skipping...')
    else:
        log.error(
            f'You do not have the right permission to run this script. Your current permission is {user_roles[0]}, '
            f'you will need to be a site admin to run this script.')
