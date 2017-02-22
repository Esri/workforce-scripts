# -*- coding: UTF-8 -*-
"""
   Copyright 2017 Esri

   Licensed under the Apache License, Version 2.0 (the "License");

   you may not use this file except in compliance with the License.

   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software

   distributed under the License is distributed on an "AS IS" BASIS,

   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

   See the License for the specific language governing permissions and

   limitations under the License.​

   This sample creates workers from CSV files
"""

import argparse
import csv
import datetime
import json
import logging
import logging.handlers
import mimetypes
import os
import traceback
import workforcehelpers


def get_workers_from_csv(csvFile, name_field="name", status_field="status", user_id_field="userId", title_field=None, contact_number_field=None):
    """
    Creates a list of dictionary objects representing workers
    :param csvFile: The CSV file to read
    :param name_field: The name of the field in the csv containing the workers name
    :param status_field: The name of the field showing the status of the worker (statuses should all be 0)
    :param user_id_field: The name of the userId field in csv file
    :param title_field: The name of the title field in csv file
    :param contact_number_field: The name of the contact number field in csv file
    :return: A list of dictionary objects representing workers
    """
    logger = logging.getLogger()
    csvFile = os.path.abspath(csvFile)
    logger.debug("Reading CSV file: {}...".format(csvFile))
    workers = []
    with open(csvFile, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            workers.append(row)

    new_workers = []
    for worker in workers:
        new_worker = dict(
            data=dict(
                attributes=dict(
                    name=worker[name_field],
                    status=worker[status_field],
                    userId=worker[user_id_field]
                )
            )
        )
        if title_field: new_worker["data"]["attributes"]["title"]=worker[title_field]
        if contact_number_field: new_worker["data"]["attributes"]["contactNumber"]=worker[contact_number_field]
        new_workers.append(new_worker)
    return new_workers


def user_exists(org_url, token, username):
    """
    Searchs the organization/portal to see if a user exists
    :param org_url: (string) The organization to search
    :param token: (string) The token to use for authentication
    :param username: (string) The username to search for
    :return: True if user exists, False if not
    """
    url = "{}/sharing/rest/community/users".format(org_url)
    params = {
        "token": token,
        "f": "json",
        "q": username
    }
    search_results = workforcehelpers.get(url, params=params)
    return username in [x["username"] for x in search_results["results"]]


def filter_workers(org_url, token, projectId, workers):
    """
    Ensures the worker is not already added and that the work has a named user
    :param org_url: (string) The organization url to use
    :param token: (string) The token to use for authentication
    :param projectId: (string) The project Id
    :param workers: List<dict> The workers to add
    :return: List<dict> The list of workers to add
    """
    # Grab the item
    logger = logging.getLogger()
    worker_fl_url = workforcehelpers.get_workers_feature_layer_url(org_url, token, projectId)
    worker_dict = workforcehelpers.query_feature_layer(worker_fl_url, token)

    workers_to_add = []
    for worker in workers:
        if not user_exists(org_url, token, worker["data"]["attributes"]["userId"]):
            logger.warning("User '{}' does not exist in your org and will not be added".format(worker["data"]["attributes"]["userId"]))
        elif worker["data"]["attributes"]["userId"] in [feature["attributes"]["userId"] for feature in worker_dict["features"]]:
            logger.warning("User '{}' is already part of this project and will not be added".format(worker["data"]["attributes"]["userId"]))
        else:
            workers_to_add.append(worker)
    return workers_to_add


def add_users_to_group(org_url, token, users, group_id):
    """
    Adds the users to the group
    :param org_url: (string) The organizational url to use
    :param token: (string) The token to authenticate with
    :param users: (list<string>) The users to add
    :param group_id: (string) The group id to add them to
    :return: The json response
    """
    logger = logging.getLogger()
    url = "{}/sharing/rest/community/groups/{}/addUsers?users={}".format(
        org_url, group_id, ",".join(users)
    )
    params = {
        "token": token,
        "f": "json"
    }
    logger.info("Adding users to group...")
    res = workforcehelpers.post(url, data=params)
    return res


def add_workers(org_url, token, projectId, workers):
    """
    Adds the workers to project
    :param org_url: (string) The organizational url to use
    :param token: (string) The token to authenticate with
    :param projectId: (string) The project Id
    :param workers: (list) The list of workers to add
    :return: The json response of the addFeatures REST API Call
    """
    logger = logging.getLogger()
    workers_url = workforcehelpers.get_workers_feature_layer_url(org_url, token, projectId)
    workers_to_post = [x["data"] for x in workers]
    add_url = "{}/addFeatures".format(workers_url)
    data = {
        'token': token,
        'f': 'json',
        'features': json.dumps(workers_to_post)
    }
    logger.debug("Adding Workers...")
    response = workforcehelpers.post(add_url, data)
    return response


def main(args):
    logger = logging.getLogger()
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    token = workforcehelpers.get_token(args.org_url, args.username, args.password)
    logger.info("Reading CSV...")
    # Next we want to parse the CSV file and create a list of workers
    workers = get_workers_from_csv(args.csvFile, args.name_field, args.status_field, args.user_id_field,
                                   args.title_field, args.contact_number_field)
    # Validate/Filter each worker
    logger.info("Validating workers...")
    workers = filter_workers(args.org_url, token, args.project_id, workers)
    if workers:
        logger.info("Adding workers...")
        response = add_workers(args.org_url, token, args.project_id, workers)
        logger.info(response)
        # Need to make sure the user is part of the workforce group
        group_id = workforcehelpers.get_group_id(args.org_url, token, args.project_id)
        worker_ids = [x["data"]["attributes"]["userId"] for x in workers]
        response = add_users_to_group(args.org_url, token, worker_ids, group_id)
        logger.info(response)
        logger.info("Completed")
    else:
        logger.info("There are no new and valid workers to add")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Add Workers to Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-url', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-pid', dest='project_id', help='The id of the project', required=True)
    parser.add_argument('-nameField', dest='name_field', help="The name of the column representing the name of the worker", required=True)
    parser.add_argument('-statusField', dest='status_field', help="The name of the column representing the status of the worker", required=True)
    parser.add_argument('-userIdField', dest='user_id_field', help="The name of the column representing the userId of the worker", required=True)
    parser.add_argument('-titleField', dest='title_field',
                        help="The name of the column representing the title of the worker", default=None)
    parser.add_argument('-contactNumberField', dest='contact_number_field',
                        help="The name of the column representing the contact number of the worker", default=None)
    parser.add_argument('-csvFile', dest='csvFile', help="The path/name of the csv file to read")
    parser.add_argument('-logFile', dest='logFile', help='The log file to use', required=True)
    args = parser.parse_args()
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
