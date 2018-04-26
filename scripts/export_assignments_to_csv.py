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

    This sample queries assignments from a workforce project and exports them to a CSV file
"""
import argparse
import logging
import logging.handlers
import traceback
import sys
import arrow
from arcgis.apps import workforce
from arcgis.gis import GIS
import csv


def log_critical_and_raise_exception(message):
    logging.getLogger().critical(message)
    raise Exception(message)


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


def main(arguments):
    # initialize logging
    logger = initialize_logging(arguments.logFile)

    # Set date params
    timezone = arguments.timezone
    date_format = arguments.dateFormat

    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = GIS(arguments.org_url, username=arguments.username, password=arguments.password,
              verify_cert=not arguments.skipSSLVerification)

    # Get the project and data
    item = gis.content.get(arguments.projectId)
    project = workforce.Project(item)

    # Query features
    logger.info("Querying features...")
    assignments = project.assignments.search(where=arguments.where)
    assignments_to_export = []
    # Take the assignment data, format it correctly if necessary, and assign it to the dict
    for assignment in assignments:
        assignment_to_export = {}
        assignment_to_export["assignedDate"] = assignment.assigned_date
        if assignment.assigned_date:
            assignment_to_export["assignedDate"] = arrow.get(assignment.assigned_date).to(timezone).strftime(
                date_format)
        if assignment.due_date:
            assignment_to_export['dueDate'] = arrow.get(assignment.due_date).to(timezone).strftime(date_format)
        if assignment.creation_date:
            assignment_to_export['CreationDate'] = arrow.get(assignment.creation_date).to(timezone).strftime(
                date_format)
        if assignment.declined_date:
            assignment_to_export['declinedDate'] = arrow.get(assignment.declined_date).to(timezone).strftime(
                date_format)
        if assignment.paused_date:
            assignment_to_export['pausedDate'] = arrow.get(assignment.paused_date).to(timezone).strftime(date_format)
        if assignment.completed_date:
            assignment_to_export['completedDate'] = arrow.get(assignment.completed_date).to(timezone).strftime(
                date_format)
        if assignment.edit_date:
            assignment_to_export['EditDate'] = arrow.get(assignment.edit_date).to(timezone).strftime(date_format)
        if assignment.in_progress_date:
            assignment_to_export['inProgressDate'] = arrow.get(assignment.in_progress_date).to(timezone).strftime(
                date_format)
        assignment_to_export["x"] = assignment.geometry["x"]
        assignment_to_export["y"] = assignment.geometry["y"]
        assignment_to_export['dispatcherId'] = assignment.dispatcher_id
        assignment_to_export['workOrderId'] = assignment.work_order_id
        assignment_to_export['description'] = assignment.status
        assignment_to_export['notes'] = assignment.notes
        assignment_to_export['priority'] = assignment.priority
        assignment_to_export['assignmentType'] = assignment.assignment_type
        assignment_to_export['workerId'] = assignment.worker_id
        assignment_to_export['GlobalID'] = assignment.global_id
        assignment_to_export['location'] = assignment.location
        assignment_to_export['Creator'] = assignment.creator
        assignment_to_export['Editor'] = assignment.editor
        assignment_to_export['dispatcherId'] = assignment.dispatcher_id
        assignment_to_export['declinedComment'] = assignment.declined_comment
        assignment_to_export['OBJECTID'] = assignment.object_id
        # Append each field to the assignments to be exported
        assignments_to_export.append(assignment_to_export)
    logger.info("write to CSV")
    # Create the CSV
    with open(arguments.outCSV, 'w', newline='') as csvfile:
        fieldnames = ["OBJECTID",
                      "x",
                      "y",
                      "description",
                      "status",
                      "notes",
                      "priority",
                      "assignmentType",
                      "workOrderId",
                      "dueDate",
                      "workerId",
                      "GlobalID",
                      "location",
                      "declinedComment",
                      "assignedDate",
                      "assignmentRead",
                      "inProgressDate",
                      "completedDate",
                      "declinedDate",
                      "pausedDate",
                      "dispatcherId",
                      "CreationDate",
                      "Creator",
                      "EditDate",
                      "Editor"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(assignments_to_export)
    logger.info("Complete")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Export assignments from Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-url', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-pid', dest='projectId', help="The id of the project to delete assignments from",
                        required=True)
    parser.add_argument('-where', dest='where', help="The where clause to use", default="1=1")
    parser.add_argument('-outCSV', dest="outCSV", help="The file/path to save the output CSV file", required=True)
    parser.add_argument('-logFile', dest="logFile", help="The file to log to", required=True)
    parser.add_argument('-outSR', dest="outSR", help="The output spatial reference to use", default=None)
    parser.add_argument('-dateFormat', dest='dateFormat', help="The date format to use", default="%m/%d/%Y %H:%M:%S")
    parser.add_argument('-timezone', dest='timezone', default="UTC", help="The timezone to export to")
    parser.add_argument('--skipSSL', dest='skipSSLVerification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
