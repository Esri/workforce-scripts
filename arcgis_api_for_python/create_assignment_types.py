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

   This sample creates assignment types from CSV files
"""

import argparse
import csv
import logging
import logging.handlers
import os
import sys
import traceback
import arcgis


def initialize_logging(log_file):
    """
    Setup logging
    :param log_file: (string) The file to log to
    :return: (Logger) a logging instance
    """
    # initialize logging
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


def get_assignment_types_from_csv(csv_file):
    """
    Creates a list of assignment types
    :param csv_file: The CSV file to read
    :return: A list assignment types
    """
    logger = logging.getLogger()
    csvFile = os.path.abspath(csv_file)
    logger.debug("Reading CSV file: {}...".format(csvFile))
    assignment_types = []
    with open(csvFile, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            assignment_types.extend(x.strip() for x in row)
    return assignment_types


def filter_assignment_types(assignment_fl, assignment_types):
    """
    Filters the assignment type, so that we don't have duplicates
    :param assignment_fl: (FeatureLayer) The assignment feature layer
    :param assignment_types: (string) The list of assignment types to add
    :return: List<dict> The list of assignment types to add
    """
    assignment_types_to_add =[]
    logger = logging.getLogger()
    for field in assignment_fl.properties["fields"]:
        if field["name"] == "assignmentType":
            for assignment_type in assignment_types:
                if assignment_types.count(assignment_type) > 1:
                    logger.critical("Duplicate types detected in csv...")
                    return []
                duplicate = False
                for current_type in field["domain"]["codedValues"]:
                    if current_type["name"] == assignment_type:
                        logger.warning("Duplicate type detected and will not be added: {}".format(assignment_type))
                        duplicate = True
                if not duplicate:
                    assignment_types_to_add.append(assignment_type)
            break
    return assignment_types_to_add


def add_assignment_types(assignment_fl, assignment_types):
    """
    Adds the assignments to project
    :param assignment_fl: (FeatureLayer) The assignment feature layer
    :param assignment_types: (list) The list of assignment types to add
    :return: The json response of the addFeatures REST API Call
    """
    for field in assignment_fl.properties["fields"]:
        if field["name"] == "assignmentType":
            length = len(field["domain"]["codedValues"])
            # Add new types here, auto-increment the coded values
            for assignment_type in assignment_types:
                field["domain"]["codedValues"].append(
                    {
                        "name": assignment_type,
                        "code": length+1
                     }
                )
                length += 1
            break
    response = assignment_fl.manager.update_definition(
        {
            'fields': assignment_fl.properties['fields']
        }
    )
    return response


def main(args):
    # initialize logging
    logger = initialize_logging(args.logFile)
    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = arcgis.gis.GIS(args.org_url, username=args.username, password=args.password)
    # Create a content manager object
    content_manager = arcgis.gis.ContentManager(gis)
    # Get the project and data
    workforce_project = content_manager.get(args.projectId)
    workforce_project_data = workforce_project.get_data()
    assignment_fl = arcgis.features.FeatureLayer(workforce_project_data["assignments"]["url"], gis)
    logger.info("Reading CSV...")
    # Next we want to parse the CSV file and create a list of assignment types
    assignment_types = get_assignment_types_from_csv(args.csvFile)
    # Validate each assignment
    logger.info("Validating assignment types...")
    assignment_types = filter_assignment_types(assignment_fl, assignment_types)
    if assignment_types:
        logger.info("Adding assignment types...")
        response = add_assignment_types(assignment_fl, assignment_types)
        logger.info(response)
        logger.info("Completed")
    else:
        logger.info("No new types to add")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Add Assignments to Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-url', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-pid', dest='projectId', help="The id of the project to add assignments to", required=True)
    parser.add_argument('-csvFile', dest='csvFile', help="The path/name of the csv file to read")
    parser.add_argument('-logFile', dest='logFile', help='The log file to use', required=True)
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
