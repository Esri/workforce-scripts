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

   This sample creates assignments from CSV files
"""

import argparse
import csv
import datetime
import logging
import logging.handlers
import mimetypes
import os
import traceback
import sys
import arcgis
import requests


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


def get_assignments_from_csv(csv_file):
    """
    Read the assignments from csv
    :param csv_file: (string) The csv file to read
    :return: List<dict> A list of dictionaries, which contain a Feature
    """
    # Parse CSV
    logger = logging.getLogger()
    csvFile = os.path.abspath(csv_file)
    logger.info("Reading CSV file: {}...".format(csvFile))
    assignments_in_csv = []
    with open(csvFile, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            assignments_in_csv.append(row)
    assignments_to_add = []
    for assignment in assignments_in_csv:
        # Create the geometry
        # "Data" stores the actual attributes and geometry we want to push
        # Anything else at the top level dictionary is meta-data for the script
        geometry = dict(x=float(assignment[args.xField]),
                        y=float(assignment[args.yField]),
                        spatialReference=dict(
                            wkid=int(args.wkid)))
        attributes = dict(assignmentType=int(assignment[args.assignmentTypeField]),
                          location=assignment[args.locationField],
                          status=0,
                          assignmentRead=None)
        if args.dispatcherIdField: attributes["dispatcherId"] = int(assignment[args.dispatcherIdField])
        if args.descriptionField: attributes["description"] = assignment[args.descriptionField]
        if args.priorityField: attributes["priority"] = int(assignment[args.priorityField])
        if args.workOrderIdField: attributes["workOrderId"] = assignment[args.workOrderIdField]
        if args.dueDateField: attributes["dueDate"] = datetime.datetime.strptime(
            assignment[args.dueDateField],
            args.dateFormat).strftime("%m/%d/%Y")
        new_assignment = arcgis.features.Feature(geometry=geometry, attributes=attributes)
        # Need this extra dictionary so we can store the attachment file with the feature
        assignment_dict = (dict(assignment=new_assignment))
        if args.attachmentFileField:
            assignment_dict["attachmentFile"] = assignment[args.attachmentFileField]
        assignments_to_add.append(assignment_dict)
    return assignments_to_add


def validate_assignments(assignment_fl, dispatcher_fl, assignments_to_add):
    """
    Checks the assignments against the dispatcher ids and against domains
    :param assignment_fl: (FeatureLayer) The feature layer containing the assignments
    :param dispatcher_fl: (FeatureLayer) The feature layer containing the dispatchers
    :param assignments_to_add: List(dict)
    :return:
    """

    # Validate Assignments
    statuses = []
    priorities = []
    assignmentTypes = []
    dispatcherIds = []

    # Get the dispatcherIds
    for dispatcher in dispatcher_fl.query().features:
        dispatcherIds.append(dispatcher.attributes["OBJECTID"])

    # Get the codes of the domains
    for field in assignment_fl.properties.fields:
        if field.name == "status":
            statuses = [cv.code for cv in field.domain.codedValues]
        if field.name == "priority":
            priorities = [cv.code for cv in field.domain.codedValues]
        if field.name == "assignmentType":
            assignmentTypes = [cv.code for cv in field.domain.codedValues]

    logging.getLogger().info("Validating assignments...")
    # check the values against the fields that have domains
    for assignment in [x["assignment"] for x in assignments_to_add]:
        if assignment.attributes["status"] not in statuses:
            logging.getLogger().critical("Invalid Status for: {}".format(assignment))
            return False
        if "priority" in assignment.attributes and assignment.attributes[
            "priority"] not in priorities:
            logging.getLogger().critical("Invalid Priority for: {}".format(assignment))
            return False
        if assignment.attributes["assignmentType"] not in assignmentTypes:
            logging.getLogger().critical("Invalid Assignment Type for: {}".format(assignment))
            return False
        if assignment.attributes["dispatcherId"] not in dispatcherIds:
            logging.getLogger().critical("Invalid Dispatcher Id for: {}".format(assignment))
            return False
    return True


def main(args):
    # initialize logging
    logger = initialize_logging(args.logFile)
    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = arcgis.gis.GIS(args.org_url, username=args.username, password=args.password)
    # Get the project and data
    workforce_project = arcgis.gis.Item(gis, args.projectId)
    workforce_project_data = workforce_project.get_data()
    assignment_fl = arcgis.features.FeatureLayer(workforce_project_data["assignments"]["url"], gis)
    dispatcher_fl = arcgis.features.FeatureLayer(workforce_project_data["dispatchers"]["url"], gis)
    assignments = get_assignments_from_csv(args.csvFile)

    # Set the dispatcher id
    id = None
    dispatchers = dispatcher_fl.query(where="userId='{}'".format(args.username))
    if dispatchers.features:
        id = dispatchers.features[0].attributes["OBJECTID"]
    else:
        logger.critical("{} is not a dispatcher".format(args.username))
        return

    # Set the dispatcherId in the assignment json
    for assignment in [x["assignment"] for x in assignments]:
        if "dispatcherId" not in assignment.attributes:
            assignment.attributes["dispatcherId"] = id

    # Add the assignments
    logger.info("Adding Assignments...")
    response = assignment_fl.edit_features(
        adds=arcgis.features.FeatureSet([x["assignment"] for x in assignments]))
    logger.info(response)
    # Assign the returned object ids to the assignment dictionary object
    for i in range(len(response["addResults"])):
        assignments[i]["assignment"].attributes["OBJECTID"] = response["addResults"][i]["objectId"]

    # Add the attachements
    logger.info("Adding Any Attachments...")
    if len(assignments) > 0 and "attachmentFile" in assignments[0]:
        for assignment in assignments:
            if assignment["attachmentFile"] and assignment["attachmentFile"] != "":
                # Need to build this part manually as the api does not support this yet
                # url to hit to add attachments (<feature-service-layer>/<object-id>/addAttachment)
                add_url = "{}/{}/addAttachment".format(workforce_project_data["assignments"]["url"],
                                                       assignment["assignment"].attributes["OBJECTID"])
                # Create the file dictionary that requests expects, guess the mimetype based on the file
                files = {"attachment": (os.path.basename(assignment["attachmentFile"]),
                                        open(os.path.abspath(assignment["attachmentFile"]), "rb"),
                                        mimetypes.guess_type(os.path.abspath(assignment["attachmentFile"])))}
                data = {
                    'f': 'json',
                    'token': gis._con._token
                }
                requests.post(add_url, data=data, files=files)
                logger.info(response)
    logger.info("Completed")

if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Add Assignments to Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-url', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-pid', dest='projectId', help="The id of the project to add assignments to", required=True)
    parser.add_argument('-xField', dest='xField', help="The field that contains the x SHAPE information", required=True)
    parser.add_argument('-yField', dest='yField', help="The field that contains the y SHAPE information", required=True)
    parser.add_argument('-assignmentTypeField', dest='assignmentTypeField',
                        help="The field that contains the assignmentType", required=True)
    parser.add_argument('-locationField', dest='locationField',
                        help="The field that contains the location", required=True)
    parser.add_argument('-dispatcherIdField', dest='dispatcherIdField',
                        help="The field that contains the dispatcherId")
    parser.add_argument('-descriptionField', dest='descriptionField', help="The field that contains the description")
    parser.add_argument('-priorityField', dest='priorityField', help="The field that contains the priority")
    parser.add_argument('-workOrderIdField', dest='workOrderIdField', help="The field that contains the workOrderId")
    parser.add_argument('-dueDateField', dest='dueDateField', help="The field that contains the dispatcherId")
    parser.add_argument('-attachmentFileField', dest='attachmentFileField',
                        help="The field that contains the file path to the attachment to upload")
    parser.add_argument('-dateFormat', dest='dateFormat', default=r"%m/%d/%Y",
                        help="The format to use for the date (eg. '%m/%d/%Y'")
    parser.add_argument('-csvFile', dest='csvFile', help="The path/name of the csv file to read")
    parser.add_argument('-wkid', dest='wkid', help='The wkid that the x,y values are use', type=int, default=4326)
    parser.add_argument('-logFile', dest='logFile', help='The log file to use', required=True)
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
