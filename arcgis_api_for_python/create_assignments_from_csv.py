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
import logging
import logging.handlers
import os
import traceback
import sys
import arcgis
import arrow
import dateutil


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
        logging.getLogger().critical("Field: {} does not exist".format(field_name))
        raise Exception("Field: {} does not exist".format(field_name))


def main(args):
    # initialize logging
    logger = initialize_logging(args.logFile)
    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = arcgis.gis.GIS(args.org_url, username=args.username, password=args.password, verify_cert=False)
    # Create a content manager object
    content_manager = arcgis.gis.ContentManager(gis)
    # Get the project and data
    workforce_project = content_manager.get(args.projectId)
    workforce_project_data = workforce_project.get_data()
    assignment_fl = arcgis.features.FeatureLayer(workforce_project_data["assignments"]["url"], gis)
    dispatcher_fl = arcgis.features.FeatureLayer(workforce_project_data["dispatchers"]["url"], gis)
    worker_fl = arcgis.features.FeatureLayer(workforce_project_data["workers"]["url"], gis)

    dispatchers = dispatcher_fl.query(where="userId='{}'".format(args.username))
    if dispatchers.features:
        dispatcher_id = dispatchers.features[0].attributes[get_field_name("OBJECTID", dispatcher_fl)]
    else:
        logger.critical("{} is not a dispatcher".format(args.username))
        return

    # Get the codes of the domains
    statuses = []
    priorities = []
    assignmentTypes = []
    for field in assignment_fl.properties.fields:
        if field.name == "status":
            statuses = [cv.code for cv in field.domain.codedValues]
        if field.name == "priority":
            priorities = [cv.code for cv in field.domain.codedValues]
        if field.name.lower() == "assignmenttype":
            assignmentTypes = [cv.code for cv in field.domain.codedValues]

    # parse the csv file
    logger.info("Reading CSV file: {}...".format(args.csvFile))
    assignments_in_csv = []
    with open(args.csvFile, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            assignments_in_csv.append(row)
    assignments_to_add = []
    for assignment in assignments_in_csv:
        # Create the geometry
        geometry = dict(x=float(assignment[args.xField]),
                        y=float(assignment[args.yField]),
                        spatialReference=dict(
                            wkid=int(args.wkid)))
        # Create the attributes
        attributes = {
            get_field_name("assignmentType", assignment_fl): int(assignment[args.assignmentTypeField]),
            get_field_name("location", assignment_fl): assignment[args.locationField],
            get_field_name("status", assignment_fl): 0,
            get_field_name("assignmentRead", assignment_fl): None
        }
        # Add optional attributes
        if args.dispatcherIdField: attributes[get_field_name("dispatcherId", assignment_fl)] = int(
            assignment[args.dispatcherIdField])
        if args.descriptionField: attributes[get_field_name("description", assignment_fl)] = assignment[
            args.descriptionField]
        if args.priorityField: attributes[get_field_name("priority", assignment_fl)] = int(
            assignment[args.priorityField])
        if args.workOrderIdField: attributes[get_field_name("workOrderId", assignment_fl)] = assignment[
            args.workOrderIdField]
        if args.dueDateField:
            d = arrow.Arrow.strptime(assignment[args.dueDateField], args.dateFormat).replace(
                tzinfo=dateutil.tz.gettz(args.timezone))
            if d.datetime.second == 0 and d.datetime.hour == 0 and d.datetime.minute == 0:
                d = d.replace(hour=23, minute=59, second=59)
            attributes[get_field_name("dueDate", assignment_fl)] = d.to('utc').timestamp * 1000
        new_assignment = arcgis.features.Feature(geometry=geometry, attributes=attributes)
        # Need this extra dictionary so we can store the attachment file with the feature
        assignment_wrapper = (dict(assignment=new_assignment))
        if args.workerField:
            assignment_wrapper["workerUsername"] = assignment[args.workerField]
        if args.attachmentFileField:
            assignment_wrapper["attachmentFile"] = assignment[args.attachmentFileField]

        # Set the dispatcherId in the assignment json
        if get_field_name("dispatcherId", assignment_fl) not in assignment_wrapper["assignment"].attributes:
            assignment_wrapper["assignment"].attributes[get_field_name("dispatcherId", assignment_fl)] = dispatcher_id

        # set worker ids
        if "workerUsername" in assignment_wrapper and assignment_wrapper["workerUsername"]:
            workers = worker_fl.query(
                where="{}='{}'".format(get_field_name("userId", worker_fl), assignment_wrapper["workerUsername"]))
            if workers.features:
                assignment_wrapper["assignment"].attributes[get_field_name("workerId", assignment_fl)] = \
                workers.features[0].attributes[get_field_name("OBJECTID", worker_fl)]
                assignment_wrapper["assignment"].attributes[get_field_name("status", assignment_fl)] = 1  # assigned
                assignment_wrapper["assignment"].attributes[
                    get_field_name("assignedDate", assignment_fl)] = arrow.now().to('utc').timestamp * 1000
            else:
                logger.critical("{} is not a worker".format(assignment_wrapper["workerUsername"]))
                return

        # Do some validation
        if assignment_wrapper["assignment"].attributes[get_field_name("status", assignment_fl)] not in statuses:
            logging.getLogger().critical("Invalid Status for: {}".format(assignment_wrapper["assignment"]))
            return
        if get_field_name("priority", assignment_fl) in assignment_wrapper["assignment"].attributes and \
                        assignment_wrapper["assignment"].attributes[
                            "priority"] not in priorities:
            logging.getLogger().critical("Invalid Priority for: {}".format(assignment_wrapper["assignment"]))
            return
        if assignment_wrapper["assignment"].attributes[
            get_field_name("assignmentType", assignment_fl)] not in assignmentTypes:
            logging.getLogger().critical("Invalid Assignment Type for: {}".format(assignment_wrapper["assignment"]))
            return
        if "attachmentFile" in assignment_wrapper and assignment_wrapper["attachmentFile"]:
            if not os.path.isfile(os.path.abspath(assignment_wrapper["attachmentFile"])):
                logging.getLogger().critical(
                    "Attachment file not found: {}".format(assignment_wrapper["attachmentFile"]))
                return
        assignments_to_add.append(assignment_wrapper)

    # Add the assignments
    logger.info("Adding Assignments...")
    response = assignment_fl.edit_features(
        adds=arcgis.features.FeatureSet([x["assignment"] for x in assignments_to_add]))
    logger.info(response)
    # Assign the returned object ids to the assignment dictionary object
    for i in range(len(response["addResults"])):
        assignments_to_add[i]["assignment"].attributes[get_field_name("OBJECTID", assignment_fl)] = \
        response["addResults"][i]["objectId"]

    # Add the attachments
    logger.info("Adding Any Attachments...")
    if len(assignments_to_add) > 0 and "attachmentFile" in assignments_to_add[0]:
        attachment_manager = arcgis.features.managers.AttachmentManager(assignment_fl)
        for assignment in assignments_to_add:
            if assignment["attachmentFile"] and assignment["attachmentFile"] != "":
                response = attachment_manager.add(
                    assignment["assignment"].attributes[get_field_name("OBJECTID", assignment_fl)],
                    os.path.abspath(assignment["attachmentFile"]))
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
    parser.add_argument('-workerField', dest='workerField', help="The field that contains the workers username")
    parser.add_argument('-attachmentFileField', dest='attachmentFileField',
                        help="The field that contains the file path to the attachment to upload")
    parser.add_argument('-dateFormat', dest='dateFormat', default="%m/%d/%Y %H:%M:%S",
                        help="The format to use for the date (eg. '%m/%d/%Y %H:%M:%S')")
    parser.add_argument('-timezone', dest='timezone', default="UTC", help="The timezone for the assignments")
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
