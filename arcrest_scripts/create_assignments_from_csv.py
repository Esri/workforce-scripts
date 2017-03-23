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


    This sample imports assignments from a csv file to a Workforce Project using the ArcREST Library
"""
import arcrest
import argparse
import csv
import logging
import logging.handlers
import os
import traceback
import arrow
import dateutil
import workforcehelpers


def get_assignments_from_csv(csvFile, xField, yField, assignmentTypeField, locationField, dispatcherIdField=None,
                             descriptionField=None, priorityField=None, workOrderIdField=None, dueDateField=None,
                             dateFormat=r"%m/%d/%Y", wkid=102100, attachmentFileField=None, workerField=None, timezone="UTC"):
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
    :param dateFormat: The format that the dueDate is in (defaults to %m/%d/%Y)
    :param wkid: The wkid that the x,y values use (defaults to 102100 which matches assignments FS)
    :param attachmentFileField: The attachment file field to use
    :param workerField: The name of the field containing the worker username
    :param timezone: The timezone the assignments are in
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
        if dispatcherIdField: new_assignment["data"]["attributes"]["dispatcherId"] = int(assignment[dispatcherIdField])
        if descriptionField: new_assignment["data"]["attributes"]["description"] = assignment[descriptionField]
        if priorityField: new_assignment["data"]["attributes"]["priority"] = int(assignment[priorityField])
        if workOrderIdField: new_assignment["data"]["attributes"]["workOrderId"] = assignment[workOrderIdField]
        if dueDateField: new_assignment["data"]["attributes"]["dueDate"] = assignment[workOrderIdField]
        if dueDateField: new_assignment["data"]["attributes"]["dueDate"] = arrow.Arrow.strptime(
            assignment[dueDateField],
            dateFormat).replace(tzinfo=dateutil.tz.gettz(timezone)).to('utc').strftime("%m/%d/%Y %H:%M:%S")
        if attachmentFileField: new_assignment["attachmentFile"] = \
            assignment[attachmentFileField].strip().rstrip()
        if workerField: new_assignment["workerUsername"] = assignment[workerField]
        assignments_out.append(new_assignment)
    return assignments_out


def validate_assignments(shh, projectId, assignments):
    """
    Validates the provided values against the codedValues specified in the FS
    :param shh: The security handler helper
    :param projectId: The project Id
    :param assignments: The list of assignments to check
    :return: True if valid, False if not
    """
    # Grab the item
    logger = logging.getLogger()
    assignment_fl = workforcehelpers.get_assignments_feature_layer(shh, projectId)
    dispatcher_fl = workforcehelpers.get_dispatchers_feature_layer(shh, projectId)
    worker_fl = workforcehelpers.get_workers_feature_layer(shh, projectId)

    statuses = []
    priorities = []
    assignmentTypes = []
    dispatcherIds = []
    workerIds = []

    # Get the dispatcherIds
    for dispatcher in dispatcher_fl.query().features:
        dispatcherIds.append(dispatcher.asDictionary["attributes"]["OBJECTID"])

    # Get the workerIds
    for worker in worker_fl.query().features:
        workerIds.append(worker.asDictionary["attributes"]["OBJECTID"])

    # Get the codes of the domains
    for field in assignment_fl.fields:
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
        if "workerUsername" in assignment and assignment["workerUsername"] and assignment["data"]["attributes"]["workerId"] not in workerIds:
            logging.getLogger().critical("Invalid Worker Id for: {}".format(assignment))
            return False
        if "attachmentFile" in assignment and assignment["attachmentFile"]:
            if not os.path.isfile(os.path.abspath(assignment["attachmentFile"])):
                logging.getLogger().critical("Attachment file not found: {}".format(assignment["attachmentFile"]))
                return False
    return True


def get_my_dispatcher_id(shh, projectId):
    """
    Get the logged in users dispatcher id
    :param shh: The ArcREST security handler helper
    :param projectId: The projectId to use
    :param username: The username of the logged in user
    :return: The OBJECTID of the specified dispatcher
    """
    logger = logging.getLogger()
    logger.debug("Getting dispatcher id for: {}...".format(shh._username))
    dispatcher_fl = workforcehelpers.get_dispatchers_feature_layer(shh, projectId)
    dispatchers = dispatcher_fl.query(where="userId='{}'".format(shh.securityhandler._username))
    if dispatchers.features:
        return dispatchers.features[0].asDictionary["attributes"]["OBJECTID"]
    else:
        logger.critical("{} is not a dispatcher".format(shh._username))
        return None


def get_worker_id(shh, worker_username, project_id):
    """
    Get the id (integer) of the worker
    :param shh: The ArcREST security handler helper
    :param project_id: (string) The projectId to use
    :param worker_username: (string) The username of the worker
    :return: (int) The id of the worker
    """
    logger = logging.getLogger()
    logger.debug("Getting worker id for: {}...".format(worker_username))
    worker_fl = workforcehelpers.get_workers_feature_layer(shh, project_id)
    workers = worker_fl.query(where="userId='{}'".format(worker_username))
    if workers.features:
        return workers.features[0].asDictionary["attributes"]["OBJECTID"]
    else:
        logger.critical("{} is not a worker".format(worker_username))
        return None


def add_assignments(shh, projectId, assignments):
    """
    Adds the assignments to project
    :param shh: The security handler helper
    :param projectId: The project Id
    :param assignments: The list of assignments to add
    :return: The json response of the addFeatures REST API Call
    """
    logger = logging.getLogger()
    assignment_fl = workforcehelpers.get_assignments_feature_layer(shh, projectId)
    features = [arcrest.common.general.Feature(x["data"]) for x in assignments]
    logger.debug("Adding Assignments...")
    response = assignment_fl.addFeature(features)
    logger.debug(response)
    # Assign the returned object ids to the assignment dictionary object
    for i in range(len(response["addResults"])):
        assignments[i]["OBJECTID"] = response["addResults"][i]["objectId"]
    # Add the attachments
    if len(assignments) > 0 and "attachmentFile" in assignments[0]:
        add_attachments(shh, projectId, assignments)
    return response


def add_attachments(shh, projectId, assignments):
    """
    Add attachments to the assignments that were added
    :param shh: The security handler helper
    :param projectId: The project Id of the workforce project
    :param assignments: The list of assignments (dictionaries)
    :return:
    """
    assignment_fl = workforcehelpers.get_assignments_feature_layer(shh, projectId)
    logging.getLogger().debug("Adding Attachments...")
    for assignment in assignments:
        if assignment["attachmentFile"] and assignment["attachmentFile"] != "":
            response = assignment_fl.addAttachment(assignment["OBJECTID"],
                                                   os.path.abspath(assignment["attachmentFile"]))
            logging.getLogger().info(response)


def main(args):
    logger = logging.getLogger()
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    shh = workforcehelpers.get_security_handler(args)
    logger.info("Reading CSV...")
    # Next we want to parse the CSV file and create a list of assignments
    assignments = get_assignments_from_csv(args.csvFile, args.xField, args.yField, args.assignmentTypeField,
                                           args.locationField, args.dispatcherIdField, args.descriptionField,
                                           args.priorityField, args.workOrderIdField, args.dueDateField,
                                           args.dateFormat, args.wkid, args.attachmentFileField, args.workerField, args.timezone)
    # If the dispatcherId Field is not present in the CSV file, then we want to use the id associated with the
    # authenticated user
    if not args.dispatcherIdField:
        logger.info("Setting dispatcher ids...")
        # Use your logged in username to get id you are associated with
        id = get_my_dispatcher_id(shh, args.projectId)
        if id is None:
            logger.critical("Dispatcher Id not found")
            return
        # Set the dispatcherId in the assignment json
        for assignment in assignments:
            if "dispatcherId" not in assignment:
                assignment["data"]["attributes"]["dispatcherId"] = id

    # Set worker ids so they will be assigned automatically
    logger.info("Setting worker ids...")
    for assignment in assignments:
        if "workerUsername" in assignment and assignment["workerUsername"]:
            id = get_worker_id(shh, assignment["workerUsername"], args.projectId)
            if id:
                assignment["data"]["attributes"]["workerId"] = id
                assignment["data"]["attributes"]["status"] = 1 # assigned
                assignment["data"]["attributes"]["assignedDate"] = arrow.now().to('utc').strftime(
                    "%m/%d/%Y %H:%M:%S")
            else:
                logger.critical("No worker id found")
                return

                # Validate each assignment
    logger.info("Validating assignments...")
    if validate_assignments(shh, args.projectId, assignments):
        logger.info("Adding Assignments...")
        response = add_assignments(shh, args.projectId, assignments)
        logger.info(response)
        logger.info("Completed")
    else:
        logger.critical("Invalid assignment detected")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Add Assignments to Workforce Project")
    parser.add_argument('-st', dest="security_type",
                        help="The security of the portal/org (Portal, LDAP, NTLM, OAuth, PKI)", default="Portal")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-url', dest='org_url', help="The url of the org/portal to use", required=True)
    parser.add_argument('-purl', dest='proxy_url', help="The proxy url to use", default=None)
    parser.add_argument('-pport', dest='proxy_port', help="The proxy port to use", default=None)
    parser.add_argument('-rurl', dest='referer_url', help="The referer url to use", default=None)
    parser.add_argument('-turl', dest='token_url', help="The token url to use", default=None)
    parser.add_argument('-cert', dest='certificate_file', help="The certificate to use", default=None)
    parser.add_argument('-kf', dest='keyfile', help="The key file to use", default=None)
    parser.add_argument('-cid', dest='client_id', help="The client id", default=None)
    parser.add_argument('-sid', dest='secret_id', help="The secret id", default=None)
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
    parser.add_argument('-wkid', dest='wkid', help='The wkid that the x,y values are use', type=int, default=102100)
    parser.add_argument('-logFile', dest='logFile', help='The log file to use', required=True)
    args = parser.parse_args()
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
