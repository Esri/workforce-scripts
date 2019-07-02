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

    This sample queries assignments from a workforce project and exports them to a CSV file
"""
import argparse
import csv
import logging
import logging.handlers
import traceback
import sys
import arrow
from arcgis.apps import workforce
from arcgis.gis import GIS


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
    logger = initialize_logging(arguments.log_file)

    # Set date params
    timezone = arguments.timezone
    date_format = arguments.date_format

    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate
    gis = GIS(arguments.org_url,
              username=arguments.username,
              password=arguments.password,
              verify_cert=not arguments.skip_ssl_verification)

    # Get the project and data
    item = gis.content.get(arguments.project_id)
    project = workforce.Project(item)

    # Query features
    logger.info("Querying features...")
    assignments = project.assignments.search(where=arguments.where)
    assignments_to_export = []
    # Take the assignment data, format it correctly if necessary, and assign it to the dict
    for assignment in assignments:
        assignment_to_export = {}
        assignment_to_export["AssignedDate"] = assignment.assigned_date
        if assignment.assigned_date:
            assignment_to_export["AssignedDate"] = \
                arrow.get(assignment.assigned_date).to(timezone).strftime(
                date_format)
        if assignment.due_date:
            assignment_to_export["DueDate"] = \
                arrow.get(assignment.due_date).to(timezone).strftime(date_format)
        if assignment.creation_date:
            assignment_to_export["CreationDate"] = \
                arrow.get(assignment.creation_date).to(timezone).strftime(
                date_format)
        if assignment.declined_date:
            assignment_to_export["DeclinedDate"] = \
                arrow.get(assignment.declined_date).to(timezone).strftime(
                date_format)
        if assignment.paused_date:
            assignment_to_export["PausedDate"] = \
                arrow.get(assignment.paused_date).to(timezone).strftime(date_format)
        if assignment.completed_date:
            assignment_to_export["CompletedDate"] = \
                arrow.get(assignment.completed_date).to(timezone).strftime(
                date_format)
        if assignment.edit_date:
            assignment_to_export["EditDate"] = \
                arrow.get(assignment.edit_date).to(timezone).strftime(date_format)
        if assignment.in_progress_date:
            assignment_to_export["InProgressDate"] = \
                arrow.get(assignment.in_progress_date).to(timezone).strftime(
                date_format)
        assignment_to_export["X"] = assignment.geometry["x"]
        assignment_to_export["Y"] = assignment.geometry["y"]
        assignment_to_export["DispatcherId"] = assignment.dispatcher_id
        assignment_to_export["WorkOrderId"] = assignment.work_order_id
        assignment_to_export["Status"] = assignment.status
        assignment_to_export["Description"] = assignment.description
        assignment_to_export["Notes"] = assignment.notes
        assignment_to_export["Priority"] = assignment.priority
        assignment_to_export["AssignmentType"] = assignment.assignment_type.name
        assignment_to_export["WorkerId"] = assignment.worker_id
        assignment_to_export["GlobalID"] = assignment.global_id
        assignment_to_export["Location"] = assignment.location
        assignment_to_export["Creator"] = assignment.creator
        assignment_to_export["Editor"] = assignment.editor
        assignment_to_export["DeclinedComment"] = assignment.declined_comment
        assignment_to_export["OBJECTID"] = assignment.object_id
        assignment_to_export["AssignmentRead"] = assignment.assignment_read
        # Append each field to the assignments to be exported
        assignments_to_export.append(assignment_to_export)
    logger.info("Writing to CSV...")
    # Create the CSV
    with open(arguments.csv_file, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["OBJECTID",
                      "X",
                      "Y",
                      "Description",
                      "Status",
                      "Notes",
                      "Priority",
                      "AssignmentType",
                      "WorkOrderId",
                      "DueDate",
                      "WorkerId",
                      "GlobalID",
                      "Location",
                      "DeclinedComment",
                      "AssignedDate",
                      "AssignmentRead",
                      "InProgressDate",
                      "CompletedDate",
                      "DeclinedDate",
                      "PausedDate",
                      "DispatcherId",
                      "CreationDate",
                      "Creator",
                      "EditDate",
                      "Editor"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(assignments_to_export)
    logger.info("Completed")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Export assignments from Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-org', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-project-id', dest='project_id', help="The id of the project to delete assignments from",
                        required=True)
    parser.add_argument('-where', dest='where', help="The where clause to use", default="1=1")
    parser.add_argument('-csv-file', dest="csv_file", help="The file/path to save the output CSV file", required=True)
    parser.add_argument('-log-file', dest="log_file", help="The file to log to", required=True)
    parser.add_argument('-date-format', dest='date_format', help="The date format to use", default="%m/%d/%Y %H:%M:%S")
    parser.add_argument('-timezone', dest='timezone', default="UTC", help="The timezone to export to")
    parser.add_argument('--skip-ssl-verification', dest='skip_ssl_verification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
