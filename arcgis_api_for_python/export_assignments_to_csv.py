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
        log_critical_and_raise_exception("Field: {} does not exist".format(field_name))


def main(arguments):
    # initialize logging
    logger = initialize_logging(arguments.logFile)

    # Set date params
    timezone = arguments.timezone
    date_format = arguments.dateFormat

    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = arcgis.gis.GIS(arguments.org_url, username=arguments.username, password=arguments.password, verify_cert= not arguments.skipSSLVerification)

    # Get the project and data
    workforce_project = gis.content.get(arguments.projectId)
    workforce_project_data = workforce_project.get_data()
    assignment_fl = arcgis.features.FeatureLayer(workforce_project_data["assignments"]["url"], gis)

    # Query features
    logger.info("Querying features...")
    assignments = assignment_fl.query(arguments.where, out_sr=arguments.outSR)
    # Convert all dates to readable format
    for assignment in assignments.features:
        # format date if there is a value
        # Divide by 1000 because REST API returns milliseconds
        if assignment.attributes[get_field_name("dueDate", assignment_fl)] and assignment.attributes[get_field_name("dueDate", assignment_fl)] != "":
            assignment.attributes[get_field_name("dueDate", assignment_fl)] = arrow.get(
                int(assignment.attributes[get_field_name("dueDate", assignment_fl)] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes[get_field_name("assignedDate", assignment_fl)] and assignment.attributes[get_field_name("assignedDate", assignment_fl)] != "":
            assignment.attributes[get_field_name("assignedDate", assignment_fl)] = arrow.get(
                int(assignment.attributes[get_field_name("assignedDate", assignment_fl)] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes[get_field_name("inProgressDate", assignment_fl)] and assignment.attributes[get_field_name("inProgressDate", assignment_fl)] != "":
            assignment.attributes[get_field_name("inProgressDate", assignment_fl)] = arrow.get(
                int(assignment.attributes[get_field_name("inProgressDate", assignment_fl)] / 1000)).to(timezone).strftime(date_format, assignment_fl)
        if assignment.attributes[get_field_name("completedDate", assignment_fl)] and assignment.attributes[get_field_name("completedDate", assignment_fl)] != "":
            assignment.attributes[get_field_name("completedDate", assignment_fl)] = arrow.get(
                int(assignment.attributes[get_field_name("completedDate", assignment_fl)] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes[get_field_name("declinedDate", assignment_fl)] and assignment.attributes[get_field_name("declinedDate", assignment_fl)] != "":
            assignment.attributes[get_field_name("declinedDate", assignment_fl)] = arrow.get(
                int(assignment.attributes[get_field_name("declinedDate", assignment_fl)] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes[get_field_name("pausedDate", assignment_fl)] and assignment.attributes[get_field_name("pausedDate", assignment_fl)] != "":
            assignment.attributes[get_field_name("pausedDate", assignment_fl)] = arrow.get(
                int(assignment.attributes[get_field_name("pausedDate", assignment_fl)] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes[get_field_name("CreationDate", assignment_fl)] and assignment.attributes[get_field_name("CreationDate", assignment_fl)] != "":
            assignment.attributes[get_field_name("CreationDate", assignment_fl)] = arrow.get(
                int(assignment.attributes[get_field_name("CreationDate", assignment_fl)] / 1000)).to(timezone).strftime(date_format)
        if assignment.attributes[get_field_name("EditDate", assignment_fl)] and assignment.attributes[get_field_name("EditDate", assignment_fl)] != "":
            assignment.attributes[get_field_name("EditDate", assignment_fl)] = arrow.get(
                int(assignment.attributes[get_field_name("EditDate", assignment_fl)] / 1000)).to(timezone).strftime(date_format)

    # workaround for saving empty feature set (there are no fields when the query returned nothing)
    if isinstance(assignments.fields, dict):
        assignments.fields = []
        assignments = inject_field_names(assignments)
    # Write the assignments to the csv file
    logging.getLogger().info("Writing to CSV...")
    assignments.save("", arguments.outCSV)
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
    parser.add_argument('--skipSSL', dest='skipSSLVerification', action='store_true', help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
