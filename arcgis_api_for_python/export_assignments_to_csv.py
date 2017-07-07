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
import arcgis
import arrow


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


def main(args):
    # initialize logging
    logger = initialize_logging(args.logFile)

    # Set date params
    timezone = args.timezone
    date_format = args.dateFormat

    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = arcgis.gis.GIS(args.org_url, username=args.username, password=args.password)

    # Get the project and data
    workforce_project = arcgis.gis.Item(gis, args.projectId)
    workforce_project_data = workforce_project.get_data()
    assignment_fl = arcgis.features.FeatureLayer(workforce_project_data["assignments"]["url"], gis)

    # Query features
    logger.info("Querying features...")
    assignments = assignment_fl.query(args.where, out_sr=args.outSR)
    # Convert all dates to readable format
    for assignment in assignments.features:
        # format date if there is a value
        # Divide by 1000 because REST API returns milliseconds
        if assignment.attributes["dueDate"] and assignment.attributes["dueDate"] != "":
            assignment.attributes["dueDate"] = arrow.get(
                int(assignment.attributes["dueDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes["assignedDate"] and assignment.attributes["assignedDate"] != "":
            assignment.attributes["assignedDate"] = arrow.get(
                int(assignment.attributes["assignedDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes["inProgressDate"] and assignment.attributes["inProgressDate"] != "":
            assignment.attributes["inProgressDate"] = arrow.get(
                int(assignment.attributes["inProgressDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes["completedDate"] and assignment.attributes["completedDate"] != "":
            assignment.attributes["completedDate"] = arrow.get(
                int(assignment.attributes["completedDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes["declinedDate"] and assignment.attributes["declinedDate"] != "":
            assignment.attributes["declinedDate"] = arrow.get(
                int(assignment.attributes["declinedDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes["pausedDate"] and assignment.attributes["pausedDate"] != "":
            assignment.attributes["pausedDate"] = arrow.get(
                int(assignment.attributes["pausedDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes["CreationDate"] and assignment.attributes["CreationDate"] != "":
            assignment.attributes["CreationDate"] = arrow.get(
                int(assignment.attributes["CreationDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes["EditDate"] and assignment.attributes["EditDate"] != "":
            assignment.attributes["EditDate"] = arrow.get(
                int(assignment.attributes["EditDate"] / 1000)).to(timezone).strftime(date_format)

    # workaround for saving empty feature set (there are no fields when the query returned nothing)
    if isinstance(assignments.fields, dict):
        assignments.fields = []
        assignments = inject_field_names(assignments)
    # Write the assignments to the csv file
    logging.getLogger().info("Writing to CSV...")
    assignments.save("", "exported.csv")
    logging.getLogger().info("Completed")


def inject_field_names(assignments):
    """
    Add the field names manually since the query did not return any features, there are no fields available
    :param assignments: (FeatureSet) The empty feature set
    :return: (FeatureSet) assignments
    """
    fields = [
        "OBJECTID",
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
        "Editor"
    ]
    for name in fields:
        assignments.fields.append({'name': name})
    return assignments


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
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
