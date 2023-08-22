#!/usr/env/bin python

import flywheel
import logging
import argparse
import os
import pandas as pd
from pathlib import Path

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

CSV_COLUMN_LIST = ['Group Name', 'Group ID', 'Project']


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


def find_or_create_group(fw_client, group_id, label):
    """
    Find or create Group indictated by "label".

    Args:
        fw_client (flywheel.Client): An active client to a Flywheel for an account with
            site-admin privileges.
        group_id (str): Instance-unique, lower-case alphabetic with "_" as id for Group.
        label (str): The Group label to find or create. Less restricted than 'id'.

    Returns:
        flywheel.Group: The found or created Group.
    """
    if not label:
        return None

    group = fw_client.groups.find_first(f"label={label}")

    if not group:
        log.info(f'Group with label "{label}" not found, creating.')
        group = flywheel.Group(id=group_id, label=label)
        _group_id = fw_client.add_group(group)
        group = fw_client.get_group(_group_id)
    else:
        log.info(f'Group with label "{label}" found.')
    if group:
        group = group.reload()

    return group


def find_or_create_project(label, group, update=True, **kwargs):
    """
    Find or create Flywheel Project with "label" under "group".

    Args:
        label (str): The Project label to find or create.
        group (flywheel.Group): The Flywheel Group object to create this Project under.
        update (bool, optional): Flag to update metadata of new or existing Project.
            Defaults to True.
        kwargs (dict): Any key/value properties of the Project you would like to update.
            Included `info` key is handled separately.
    Returns:
        flywheel.Project: The found or created Flywheel Project object.
    """
    if not label:
        return None

    # group = fw_client.get_group(group_id)

    project = group.projects.find_first(f"label={label}")

    if not project:
        log.info(f'Project with label "{label}" not found, creating.')
        project = group.add_project(label=label)
    else:
        log.info(f'Project with label "{label}" found.')

    if project:
        if update and kwargs:
            # Check for info, separate update process
            if "info" in kwargs:
                info = kwargs.pop("info")
                project.update_info(info)
            # Check for empty dictionary
            if kwargs:
                project.update(**kwargs)

        project = project.reload()

    return project


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a program to find or create group and project container in '
                                                 'your Instance.\nThis program is designed for Site Admin user only. It '
                                                 'required API Key and CSV file as input.\nExample Code:\n\tpython '
                                                 'path/to/create-group-project.py --key <your-api-key-here> --file '
                                                 'path/to/group-project-list.csv')
    parser.add_argument('--key', dest='api_key', metavar='Key', help='API Key')

    parser.add_argument('--file', dest='input', required=True, type=validate_file_type, help='CSV File to find or '
                                                                                             'create group and '
                                                                                             'project container',
                        metavar='CSV File')

    args = parser.parse_args()

    fw = flywheel.Client(args.api_key)

    user_roles = fw.get_current_user().roles

    if 'site_admin' in user_roles:

        df = pd.read_csv(Path(args.input)).dropna(how='all')
        # Group Name,Group ID,Project
        for (index, group_name, group_id, project) in df.itertuples():
            if not pd.isna(group_name) and not pd.isna(group_id) and not pd.isna(project):
                # create group
                group_container = find_or_create_group(fw, group_id.strip().lower(), group_name.strip().upper())

                # create project
                project_container = find_or_create_project(project, group_container, update=False)
