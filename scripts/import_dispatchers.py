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

   This sample creates dispatchers from a CSV file
"""

import argparse
import csv
import logging
import logging.handlers
import os
import sys
import traceback
from arcgis.apps import workforce
from arcgis.gis import GIS


def initialize_logger(log_file):
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
    rh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10485760)
    rh.setFormatter(formatter)
    rh.setLevel(logging.DEBUG)
    # Add the handlers to the root logger
    logger.addHandler(sh)
    logger.addHandler(rh)
    return logger


def main(arguments):
    # Initialize logging
    logger = initialize_logger(arguments.log_file)
    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = GIS(arguments.org_url,
              username=arguments.username,
              password=arguments.password,
              verify_cert=not arguments.skip_ssl_verification)
    # Get the workforce project
    item = gis.content.get(arguments.project_id)
    project = workforce.Project(item)
    # Read the CVS file and loop through the dispatchers information contained within this file
    logger.info("Parsing CSV...")
    with open(os.path.abspath(arguments.csv_file), 'r') as file:
        reader = csv.DictReader(file)
        # List of dispatchers to add
        dispatchers = []
        for row in reader:
            # Create a dispatcher using the required fields
            dispatcher = workforce.Dispatcher(project,
                                              name=row[arguments.name_field],
                                              user_id=row[arguments.user_id_field])
            # These fields are optional, and are added separately
            if arguments.contact_number_field:
                dispatcher.contact_number = row.get(arguments.contact_number_field)
            dispatchers.append(dispatcher)
        # Batch add dispatchers
        logger.info("Adding Workers...")
        project.dispatchers.batch_add(dispatchers)
    logger.info("Completed")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Add Dispatchers to Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-org', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-project-id', dest='project_id', help='The id of the project', required=True)
    parser.add_argument('-name-field', dest='name_field',
                        help="The name of the column representing the name of the dispatcher", required=True)
    parser.add_argument('-user-id-field', dest='user_id_field',
                        help="The name of the column representing the userId of the dispatcher", required=True)
    parser.add_argument('-contact-number-field', dest='contact_number_field',
                        help="The name of the column representing the contact number of the dispatcher", default=None)
    parser.add_argument('-csv-file', dest='csv_file', help="The path/name of the csv file to read")
    parser.add_argument('-log-file', dest='log_file', help='The log file to use', required=True)
    parser.add_argument('--skip-ssl-verification', dest='skip_ssl_verification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
