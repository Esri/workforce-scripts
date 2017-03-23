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
import logging
import logging.handlers
import traceback
import arrow
import workforcehelpers


def write_assignments_to_csv(csv_file, assignments, date_format="%d/%m/%Y %H:%M:%S", timezone="UTC"):
    """
    Writes the list of assignments to a CSV file
    :param csv_file: The file to write to
    :param assignments: The list of assignments to write
    :param date_format: The format to use for the dates
    :param timezone: The timezone to use
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
    # convert assignment features to dictionaries
    assignments = [a.asDictionary for a in assignments]
    for assignment in assignments:
        # Add the geometry attributes to the 'attributes' section of the dictionary
        assignment["attributes"]["x"] = assignment["geometry"]["x"]
        assignment["attributes"]["y"] = assignment["geometry"]["y"]
        # format date if there is a value
        # Divide by 1000 because REST API returns milliseconds
        if assignment["attributes"]["dueDate"] and assignment["attributes"]["dueDate"] != "":
            assignment["attributes"]["dueDate"] = arrow.get(
                int(assignment["attributes"]["dueDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment["attributes"]["assignedDate"] and assignment["attributes"]["assignedDate"] != "":
            assignment["attributes"]["assignedDate"] = arrow.get(
                int(assignment["attributes"]["assignedDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment["attributes"]["inProgressDate"] and assignment["attributes"]["inProgressDate"] != "":
            assignment["attributes"]["inProgressDate"] = arrow.get(
                int(assignment["attributes"]["inProgressDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment["attributes"]["completedDate"] and assignment["attributes"]["completedDate"] != "":
            assignment["attributes"]["completedDate"] = arrow.get(
                int(assignment["attributes"]["completedDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment["attributes"]["declinedDate"] and assignment["attributes"]["declinedDate"] != "":
            assignment["attributes"]["declinedDate"] = arrow.get(
                int(assignment["attributes"]["declinedDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment["attributes"]["pausedDate"] and assignment["attributes"]["pausedDate"] != "":
            assignment["attributes"]["pausedDate"] = arrow.get(
                int(assignment["attributes"]["pausedDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment["attributes"]["CreationDate"] and assignment["attributes"]["CreationDate"] != "":
            assignment["attributes"]["CreationDate"] = arrow.get(
                int(assignment["attributes"]["CreationDate"] / 1000)).to(timezone).strftime(date_format)
        if assignment["attributes"]["EditDate"] and assignment["attributes"]["EditDate"] != "":
            assignment["attributes"]["EditDate"] = arrow.get(
                int(assignment["attributes"]["EditDate"] / 1000)).to(timezone).strftime(date_format)
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
    shh = workforcehelpers.get_security_handler(args)
    # Get the assignment feature layer
    logging.getLogger().info("Getting assignment feature layer...")
    assignment_fl = workforcehelpers.get_assignments_feature_layer(shh, args.projectId)
    # Query the assignment feature layer to get certain assignments
    logging.getLogger().info("Querying assignments...")
    assignments = assignment_fl.query(where=args.where, out_fields="*", outSR=args.outSR).features
    # Write the assignments to the csv file
    logging.getLogger().info("Writing to CSV...")
    write_assignments_to_csv(args.outCSV, assignments, args.dateFormat, args.timezone)
    logging.getLogger().info("Completed")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Export assignments from Workforce Project")
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
    parser.add_argument('-pid', dest='projectId', help="The id of the project to delete assignments from",
                        required=True)
    parser.add_argument('-where', dest='where', help="The where clause to use", default="1=1")
    parser.add_argument('-outCSV', dest="outCSV", help="The file/path to save the output CSV file", required=True)
    parser.add_argument('-logFile', dest="logFile", help="The file to log to",required=True)
    parser.add_argument('-outSR', dest="outSR", help="The output spatial reference to use", default=None)
    parser.add_argument('-dateFormat', dest='dateFormat', help="The date format to use", default="%d/%m/%Y %H:%M:%S")
    parser.add_argument('-timezone', dest='timezone', default="UTC", help="The timezone to export to")
    args = parser.parse_args()
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))