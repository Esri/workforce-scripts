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

    This sample queries assignments from a workforce project and exports them to a CSV file
"""
import argparse
import csv
import datetime
import logging
import logging.handlers
import traceback
import workforcehelpers


def write_assignments_to_csv(csv_file, assignments, date_format="%d/%m/%Y %H:%M:%S" ):
    """
    Writes the list of assignments to a CSV file
    :param csv_file: The file to write to
    :param assignments: The list of assignments to write
    :param date_format: The format to use for the dates
    :return:
    """

    # (date values are stored as unix timestamp (number of milliseconds since 1/1/1970) in AGOL)
    # The the field names and order in which to write them to the CSV
    field_names = [
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
    for assignment in assignments:
        # Add the geometry attributes to the 'attributes' section of the dictionary
        assignment["attributes"]["x"] = assignment["geometry"]["x"]
        assignment["attributes"]["y"] = assignment["geometry"]["y"]
        # format date if there is a value
        # Divide by 1000 because REST API returns milliseconds
        if assignment["attributes"]["dueDate"] and assignment["attributes"]["dueDate"] != "":
            assignment["attributes"]["dueDate"] = datetime.datetime.utcfromtimestamp(
                int(assignment["attributes"]["dueDate"] / 1000)).strftime(date_format)
        if assignment["attributes"]["assignedDate"] and assignment["attributes"]["assignedDate"] != "":
            assignment["attributes"]["assignedDate"] = datetime.datetime.utcfromtimestamp(
                int(assignment["attributes"]["assignedDate"] / 1000)).strftime(date_format)
        if assignment["attributes"]["inProgressDate"] and assignment["attributes"]["inProgressDate"] != "":
            assignment["attributes"]["inProgressDate"] = datetime.datetime.utcfromtimestamp(
                int(assignment["attributes"]["inProgressDate"] / 1000)).strftime(date_format)
        if assignment["attributes"]["completedDate"] and assignment["attributes"]["completedDate"] != "":
            assignment["attributes"]["completedDate"] = datetime.datetime.utcfromtimestamp(
                int(assignment["attributes"]["completedDate"] / 1000)).strftime(date_format)
        if assignment["attributes"]["declinedDate"] and assignment["attributes"]["declinedDate"] != "":
            assignment["attributes"]["declinedDate"] = datetime.datetime.utcfromtimestamp(
                int(assignment["attributes"]["declinedDate"] / 1000)).strftime(date_format)
        if assignment["attributes"]["pausedDate"] and assignment["attributes"]["pausedDate"] != "":
            assignment["attributes"]["pausedDate"] = datetime.datetime.utcfromtimestamp(
                int(assignment["attributes"]["pausedDate"] / 1000)).strftime(date_format)
        if assignment["attributes"]["CreationDate"] and assignment["attributes"]["CreationDate"] != "":
            assignment["attributes"]["CreationDate"] = datetime.datetime.utcfromtimestamp(
                int(assignment["attributes"]["CreationDate"] / 1000)).strftime(date_format)
        if assignment["attributes"]["EditDate"] and assignment["attributes"]["EditDate"] != "":
            assignment["attributes"]["EditDate"] = datetime.datetime.utcfromtimestamp(
                int(assignment["attributes"]["EditDate"] / 1000)).strftime(date_format)
    # Make a list of the assignments (list of dictionaries) where each dictionary is the attributes of the feature
    assignment_attributes = [a['attributes'] for a in assignments]
    logging.getLogger().debug("Writing assignments to CSV file: {}".format(csv_file))
    # Write to the CSV file
    with open(csv_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=field_names, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(assignment_attributes)


def main(args):
    # First step is to authenticate and get a valid token
    logging.getLogger().info("Authenticating...")
    token = workforcehelpers.get_token(args.org_url, args.username, args.password)
    # Get the assignment feature layer
    logging.getLogger().info("Getting assignment feature layer...")
    assignment_fl_url = workforcehelpers.get_assignments_feature_layer_url(args.org_url, token, args.projectId)
    # Query the assignment feature layer to get certain assignments
    logging.getLogger().info("Querying assignments...")
    assignments = workforcehelpers.query_feature_layer(assignment_fl_url, token, where=args.where, outSR=args.outSR)["features"]
    # Write the assignments to the csv file
    logging.getLogger().info("Writing to CSV...")
    write_assignments_to_csv(args.outCSV, assignments, args.dateFormat)
    logging.getLogger().info("Completed")


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
    parser.add_argument('-dateFormat', dest='dateFormat', help="The date format to use", default="%d/%m/%Y %H:%M:%S")
    args = parser.parse_args()
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))