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
import logging
import logging.handlers
import os
import sys
import traceback
import arcgis


def log_critical_and_raise_exception(message):
    logging.getLogger().critical(message)
    raise Exception(message)


def user_exists(gis, username):
    """
    Searchs the organization/portal to see if a user exists
    :param gis: (GIS) The gis to use for searching
    :param username: (string) The username to search for
    :return: True if user exists, False if not
    """
    users = gis.users.search(query=username)
    return username in [x["username"] for x in users]


def get_field_name(field_name, fl):
    """
    Attempts to get the field name (could vary based on portal/AGOL implementation)
    :param field_name: (string) The field name to get
    :param fl: (FeatureLayer) The feature layer the field should be in
    :return: (string) The field name
    """
    for field in fl.properties["fields"]:
        if field_name == field["name"]:
            return field_name
        if field_name.lower() == field["name"]:
            return field_name.lower()
        # These field names are not only lower case but also different for Portal vs AGOL
        # CreationDate
        if field_name == "CreationDate":
            return fl.properties["editFieldsInfo"]["creationDateField"]
        # EditDate
        if field_name == "EditDate":
            return fl.properties["editFieldsInfo"]["editDateField"]
        # Creator
        if field_name == "Creator":
            return fl.properties["editFieldsInfo"]["creatorField"]
        # Editor
        if field_name == "Editor":
            return fl.properties["editFieldsInfo"]["editorField"]
    else:
        log_critical_and_raise_exception("Field: {} does not exist".format(field_name))


def initialize_logger(logFile):
    # Format the logger
    # The format for the logs
    formatter = logging.Formatter("[%(asctime)s] [%(filename)30s:%(lineno)4s - %(funcName)30s()]\
                     [%(threadName)5s] [%(name)10.10s] [%(levelname)8s] %(message)s")
    # Grab the root logger
    logger = logging.getLogger()
    # Set the root logger logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.DEBUG)
    # Create a handler to print to the console
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    # Create a handler to log to the specified file
    rh = logging.handlers.RotatingFileHandler(logFile, mode='a', maxBytes=10485760)
    rh.setFormatter(formatter)
    rh.setLevel(logging.DEBUG)
    # Add the handlers to the root logger
    logger.addHandler(sh)
    logger.addHandler(rh)
    return logger


def main(arguments):
    # initialize logging
    logger = initialize_logger(arguments.logFile)
    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = arcgis.gis.GIS(arguments.org_url, username=arguments.username, password=arguments.password, verify_cert= not arguments.skipSSLVerification)
    # Get the project and data
    workforce_project = gis.content.get(args.project_id)
    workforce_project_data = workforce_project.get_data()
    workers_fl = arcgis.features.FeatureLayer(workforce_project_data["workers"]["url"], gis)
    current_workers = workers_fl.query().features

    logger.info("Reading CSV...")
    # Next we want to parse the CSV file and create a list of workers
    csvFile = os.path.abspath(arguments.csvFile)
    workers = []
    with open(csvFile, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            new_worker_attributes = {
                get_field_name("name", workers_fl): row[arguments.name_field],
                get_field_name("status", workers_fl): row[arguments.status_field],
                get_field_name("userId", workers_fl): row[arguments.user_id_field]
            }
            if arguments.title_field: new_worker_attributes[get_field_name("title", workers_fl)] = row[arguments.title_field]
            if arguments.contact_number_field: new_worker_attributes[get_field_name("contactNumber", workers_fl)] = row[
                arguments.contact_number_field]
            new_worker = arcgis.features.Feature(attributes=new_worker_attributes)
            # check if the user exists in the org
            if not user_exists(gis, new_worker.attributes[get_field_name("userId", workers_fl)]):
                log_critical_and_raise_exception("User '{}' does not exist in your org".format(
                    new_worker.attributes[get_field_name("userId", workers_fl)]))
            # check if user already is part of the project
            elif new_worker.attributes[get_field_name("userId", workers_fl)] in [
                w.attributes[get_field_name("userId", workers_fl)] for w in current_workers]:
                log_critical_and_raise_exception("User '{}' is already part of this project".format(
                    new_worker.attributes[get_field_name("userId", workers_fl)]))
            else:
                workers.append(new_worker)
    # make sure we have workers to add
    if workers:
        logger.info("Adding workers...")
        response = workers_fl.edit_features(adds=arcgis.features.FeatureSet(workers))
        logger.info(response)
        # Need to make sure the user is part of the workforce group
        worker_ids = [x.attributes[get_field_name("userId", workers_fl)] for x in workers]
        group = gis.groups.get(workforce_project_data["groupId"])
        logger.info("Adding workers to project group...")
        response = group.add_users(worker_ids)
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
    parser.add_argument('-nameField', dest='name_field',
                        help="The name of the column representing the name of the worker", required=True)
    parser.add_argument('-statusField', dest='status_field',
                        help="The name of the column representing the status of the worker", required=True)
    parser.add_argument('-userIdField', dest='user_id_field',
                        help="The name of the column representing the userId of the worker", required=True)
    parser.add_argument('-titleField', dest='title_field',
                        help="The name of the column representing the title of the worker", default=None)
    parser.add_argument('-contactNumberField', dest='contact_number_field',
                        help="The name of the column representing the contact number of the worker", default=None)
    parser.add_argument('-csvFile', dest='csvFile', help="The path/name of the csv file to read")
    parser.add_argument('-logFile', dest='logFile', help='The log file to use', required=True)
    parser.add_argument('--skipSSL', dest='skipSSLVerification', action='store_true', help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
