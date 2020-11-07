# -*- coding: UTF-8 -*-
"""
   Copyright 2018 Esri

   Licensed under the Apache License, Version 2.0 (the "License");

   you may not use this file except in compliance with the License.

   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software

   distributed under the License is distributed on an "AS IS" BASIS,

   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

   See the License for the specific language governing permissions and

   limitations under the License.​

   This sample creates assignment types from CSV files
"""

import argparse
import csv
import logging
import logging.handlers
import os
import sys
import traceback
from arcgis.gis import GIS
from arcgis.apps import workforce


def initialize_logging(log_file=None):
    """
    Setup logging
    :param log_file: (string) The file to log to
    :return: (Logger) a logging instance
    """
    # initialize logging
    formatter = logging.Formatter(
        "[%(asctime)s] [%(filename)30s:%(lineno)4s - %(funcName)30s()][%(threadName)5s] [%(name)10.10s] [%(levelname)8s] %(message)s")
    # Grab the root logger
    logger = logging.getLogger()
    # Set the root logger logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.DEBUG)
    # Create a handler to print to the console
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    # Create a handler to log to the specified file
    if log_file:
        rh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10485760)
        rh.setFormatter(formatter)
        rh.setLevel(logging.DEBUG)
        logger.addHandler(rh)
    # Add the handlers to the root logger
    logger.addHandler(sh)
    return logger


def get_assignment_types_from_csv(csv_file):
    """
    Creates a list of assignment types
    :param csv_file: The CSV file to read
    :return: A list assignment types
    """
    logger = logging.getLogger()
    csv_file = os.path.abspath(csv_file)
    logger.debug("Reading CSV file: {}...".format(csv_file))
    assignment_types = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            assignment_types.extend(x.strip() for x in row)
    return assignment_types


def main(arguments):
    # initialize logging
    logger = initialize_logging(arguments.log_file)

    # Create the GIS
    logger.info("Authenticating...")

    # Get the project and data
    gis = GIS(arguments.org_url,
              username=arguments.username,
              password=arguments.password,
              verify_cert=not arguments.skip_ssl_verification)
    item = gis.content.get(arguments.project_id)
    project = workforce.Project(item)

    logger.info("Reading CSV...")
    # Next we want to parse the CSV file and create a list of assignment types
    assignment_types = get_assignment_types_from_csv(arguments.csv_file)
    assignment_types_to_add = []
    for at in assignment_types:
        assignment_types_to_add.append(workforce.AssignmentType(project, name=at))
    logger.info("Adding Assignment Types...")
    project.assignment_types.batch_add(assignment_types_to_add)
    logger.info("Completed")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Add Assignments to Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-org', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-project-id', dest='project_id', help="The id of the project to add assignments to", required=True)
    parser.add_argument('-csv-file', dest='csv_file', help="The path/name of the csv file to read", required=True)
    parser.add_argument('-log-file', dest='log_file', help='The log file to use')
    parser.add_argument('--skip-ssl-verification', dest='skip_ssl_verification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
