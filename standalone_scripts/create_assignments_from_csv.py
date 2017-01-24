# -*- coding: UTF-8 -*-
"""
   Copyright 2016 Esri

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
import json
import logging
import logging.handlers
import mimetypes
import os
import traceback
import workforcehelpers
import arrow


def get_assignments_from_csv(csvFile, xField, yField, assignmentTypeField, locationField, dispatcherIdField=None,
                             descriptionField=None, priorityField=None, workOrderIdField=None, dueDateField=None,
                             dateFormat=r"%m/%d/%Y %H:%M", wkid=102100, attachmentFileField=None):
    """
    Creates a list of dictionary objects representing assignments
    :param csvFile: The CSV file to read
    :param xField: The name of field containing the x geometry
    :param yField: The name of the field containing y geometry
    :param assignmentTypeField: The name of the field containing the assignmentType
    :param locationField: The name of the field containing the location
    :param dispatcherIdField: The name of the field containing the dispatcherId
    :param descriptionField: The name of the field containing the description
    :param priorityField: The name of the field containing the priority
    :param workOrderIdField: The name of the filed containing the workOrderId
    :param dueDateField: The name of the field containing the dueDate
    :param dateFormat: The format that the dueDate is in (defaults to %m/%d/%Y %H:%M)
    :param wkid: The wkid that the x,y values use (defaults to 102100 which matches assignments FS)
    :param attachmentFileField: The attachment file field to use
    :return: A list of dictionary objects representing assignments
    """
    logger = logging.getLogger()
    csvFile = os.path.abspath(csvFile)
    logger.debug("Reading CSV file: {}...".format(csvFile))
    assignments_in_csv = []
    with open(csvFile, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            assignments_in_csv.append(row)

    assignments_out = []
    for assignment in assignments_in_csv:
        # New assignments should have unassigned status, and be unread
        new_assignment = dict(data=dict(attributes=dict(status=0, assignmentRead=None)))
        # Create the geometry
        # "Data" stores the actual attributes and geometry we want to push
        # Anything else at the top level dictionary is meta-data for the script
        new_assignment["data"]["geometry"] = dict(x=float(assignment[xField]), y=float(assignment[yField]),
                                                  spatialReference=dict(wkid=int(wkid)))
        new_assignment["data"]["attributes"]["assignmentType"] = int(assignment[assignmentTypeField])
        new_assignment["data"]["attributes"]["location"] = assignment[locationField]
        if dispatcherIdField: new_assignment["data"]["attributes"]["dispatcherId"] = assignment[dispatcherIdField]
        if descriptionField: new_assignment["data"]["attributes"]["description"] = assignment[descriptionField]
        if priorityField: new_assignment["data"]["attributes"]["priority"] = int(assignment[priorityField])
        if workOrderIdField: new_assignment["data"]["attributes"]["workOrderId"] = int(assignment[workOrderIdField])
        if dueDateField: new_assignment["data"]["attributes"]["dueDate"] = arrow.Arrow.strptime(
            assignment[dueDateField],
            dateFormat).to('utc').strftime("%m/%d/%Y %H:%M")
        if attachmentFileField: new_assignment["attachmentFile"] = \
            assignment[attachmentFileField].strip().rstrip()
        assignments_out.append(new_assignment)
    return assignments_out


def validate_assignments(org_url, token, projectId, assignments):
    """
    Validates the provided values against the codedValues specified in the FS
    :param org_url: (string) The organization url to use
    :param token: (string) The token to use for authentication
    :param projectId: (string) The project Id
    :param assignments: (string) The list of assignments to check
    :return: True if valid, False if not
    """
    # Grab the item
    logger = logging.getLogger()
    assignment_fl = workforcehelpers.get_assignments_feature_layer_url(org_url, token, projectId)
    dispatcher_fl = workforcehelpers.get_dispatchers_feature_layer_url(org_url, token, projectId)
    dispatchers = workforcehelpers.query_feature_layer(dispatcher_fl, token)

    statuses = []
    priorities = []
    assignmentTypes = []
    dispatcherIds = []

    # Get the dispatcherIds
    for dispatcher in dispatchers["features"]:
        dispatcherIds.append(dispatcher["attributes"]["OBJECTID"])

    # Get the codes of the domains
    for field in workforcehelpers.get_feature_layer(assignment_fl, token)["fields"]:
        if field["name"] == "status":
            statuses = [cv["code"] for cv in field["domain"]["codedValues"]]
        if field["name"] == "priority":
            priorities = [cv["code"] for cv in field["domain"]["codedValues"]]
        if field["name"] == "assignmentType":
            assignmentTypes = [cv["code"] for cv in field["domain"]["codedValues"]]

    logger.debug("Validating assignments...")
    # check the values against the fields that have domains
    for assignment in assignments:
        if assignment["data"]["attributes"]["status"] not in statuses:
            logging.getLogger().critical("Invalid Status for: {}".format(assignment))
            return False
        if "priority" in assignment["data"]["attributes"] and assignment["data"]["attributes"][
            "priority"] not in priorities:
            logging.getLogger().critical("Invalid Priority for: {}".format(assignment))
            return False
        if assignment["data"]["attributes"]["assignmentType"] not in assignmentTypes:
            logging.getLogger().critical("Invalid Assignment Type for: {}".format(assignment))
            return False
        if assignment["data"]["attributes"]["dispatcherId"] not in dispatcherIds:
            logging.getLogger().critical("Invalid Dispatcher Id for: {}".format(assignment))
            return False
        if "attachmentFile" in assignment and assignment["attachmentFile"]:
            if not os.path.isfile(os.path.abspath(assignment["attachmentFile"])):
                logging.getLogger().critical("Attachment file not found: {}".format(assignment["attachmentFile"]))
                return False
    return True


def get_dispatcher_id(org_url, token, username, projectId):
    """
    Get the logged in users dispatcher id
    :param org_url: (string) The organizational url to use
    :param token: (string) The token to authenticate with
    :param projectId: (string) The projectId to use
    :param username: (string) The username of the logged in user
    :return: The OBJECTID of the specified dispatcher
    """
    logger = logging.getLogger()
    logger.debug("Getting dispatcher id for: {}...".format(username))
    dispatcher_fl = workforcehelpers.get_dispatchers_feature_layer_url(org_url, token, projectId)
    dispatchers = workforcehelpers.query_feature_layer(dispatcher_fl, token, where="userId='{}'".format(username))
    if dispatchers["features"]:
        return dispatchers["features"][0]["attributes"]["OBJECTID"]
    else:
        logger.critical("{} is not a dispatcher".format(username))
        return None


def add_assignments(org_url, token, projectId, assignments):
    """
    Adds the assignments to project
    :param org_url: (string) The organizational url to use
    :param token: (string) The token to authenticate with
    :param projectId: (string) The project Id
    :param assignments: (list) The list of assignments to add
    :return: The json response of the addFeatures REST API Call
    """
    logger = logging.getLogger()
    assignments_url = workforcehelpers.get_assignments_feature_layer_url(org_url, token, projectId)
    assignment_to_post = [x["data"] for x in assignments]
    add_url = "{}/addFeatures".format(assignments_url)
    data = {
        'token': token,
        'f': 'json',
        'features': json.dumps(assignment_to_post)
    }
    logger.debug("Adding Assignments...")
    response = workforcehelpers.post(add_url, data)
    # Assign the returned object ids to the assignment dictionary object
    for i in range(len(response["addResults"])):
        assignments[i]["OBJECTID"] = response["addResults"][i]["objectId"]
    # Add the attachments
    if len(assignments) > 0 and "attachmentFile" in assignments[0]:
        add_attachments(org_url, token, projectId, assignments)
    return response


def add_attachments(org_url, token, projectId, assignments):
    """
    This adds attachments to the assignments if they have one
    :param org_url: The org url to use
    :param token: The token to authenticate with
    :param projectId: The project Id to use
    :param assignments: The list of assignment json objects
    :return:
    """
    assignment_fl_url = workforcehelpers.get_assignments_feature_layer_url(org_url, token, projectId)
    logging.getLogger().debug("Adding Attachments...")
    for assignment in assignments:
        if assignment["attachmentFile"] and assignment["attachmentFile"] != "":
            # url to hit to add attachments (<feature-service-layer>/<object-id>/addAttachment)
            add_url = "{}/{}/addAttachment".format(assignment_fl_url, assignment["OBJECTID"])
            # Create the file dictionary that requests expects, guess the mimetype based on the file
            files = {"attachment": (os.path.basename(assignment["attachmentFile"]),
                                    open(os.path.abspath(assignment["attachmentFile"]), "rb"),
                                    mimetypes.guess_type(os.path.abspath(assignment["attachmentFile"])))}
            data = {
                'f': 'json',
                'token': token
            }
            response = workforcehelpers.post(add_url, data, files)
            logging.getLogger().debug(response)


def main(args):
    logger = logging.getLogger()
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    token = workforcehelpers.get_token(args.org_url, args.username, args.password)
    logger.info("Reading CSV...")
    # Next we want to parse the CSV file and create a list of assignments
    assignments = get_assignments_from_csv(args.csvFile, args.xField, args.yField, args.assignmentTypeField,
                                           args.locationField, args.dispatcherIdField, args.descriptionField,
                                           args.priorityField, args.workOrderIdField, args.dueDateField,
                                           args.dateFormat, args.wkid, args.attachmentFileField)
    # If the dispatcherId Field is not present in the CSV file, then we want to use the id associated with the
    # authenticated user
    if not args.dispatcherIdField:
        logger.info("Setting dispatcher ids...")
        # Use your logged in username to get id you are associated with
        id = get_dispatcher_id(args.org_url, token, args.username, args.projectId)
        if id is None:
            logger.critical("Dispatcher Id not found")
            return
        # Set the dispatcherId in the assignment json
        for assignment in assignments:
            if "dispatcherId" not in assignment["data"]["attributes"]:
                assignment["data"]["attributes"]["dispatcherId"] = id
    # Validate each assignment
    logger.info("Validating assignments...")
    if validate_assignments(args.org_url, token, args.projectId, assignments):
        logger.info("Adding Assignments...")
        response = add_assignments(args.org_url, token, args.projectId, assignments)
        logger.info(response)
        logger.info("Completed")
    else:
        logger.critical("Invalid assignment detected")


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
    parser.add_argument('-dateFormat', dest='dateFormat', default=r"%m/%d/%Y %H:%M",
                        help="The format to use for the date (eg. '%m/%d/%Y %H:%M'")
    parser.add_argument('-csvFile', dest='csvFile', help="The path/name of the csv file to read")
    parser.add_argument('-wkid', dest='wkid', help='The wkid that the x,y values are use', type=int, default=4326)
    parser.add_argument('-logFile', dest='logFile', help='The log file to use', required=True)
    args = parser.parse_args()
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
