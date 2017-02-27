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

    This sample copies assignments from one project to another feature service
"""
import argparse
import json
import logging
import logging.handlers
import traceback
import sys
import arcgis


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


def validate_config(target_fl, field_mappings):
    """
    Validates the field mappings to make sure the fields exist
    :param target_fl: (string) The feature service to copy to
    :param field_mappings: (dict) The field mappings
    :return: True if valid, False if not
    """
    logging.getLogger().info("Validating field mappings...")
    # Validate configuration file
    fields = ["OBJECTID",
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
    # Get the names of the fields in the target layer
    target_fields = target_fl.properties.fields
    field_names = [field["name"] for field in target_fields]
    # Check that the configuration file is not missing any fields
    for field in fields:
        if field not in field_mappings:
            logging.getLogger().critical("Config file is missing: '{}' field mapping".format(field))
            return False
    # Check that the provided fields exist in the target feature layer
    for field in field_mappings.values():
        if field not in field_names:
            logging.getLogger().critical("Field '{}' is not present in the provided target feature layer".format(field))
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
    target_fl = arcgis.features.FeatureLayer(args.targetFL, gis)

    # Open the field mappings config file
    logging.getLogger().info("Reading field mappings...")
    with open(args.configFile, 'r') as f:
        field_mappings = json.load(f)
    logging.getLogger().info("Validating field mappings...")
    if not validate_config(target_fl, field_mappings):
        logger.critical("Invalid field mappings detected")
        return
    else:
        # Copy the assignments
        # Query the source to get the features specified by the query string
        logger.info("Querying source features...")
        current_assignments = assignment_fl.query(where=args.where, out_sr=target_fl.properties.extent.spatialReference)

        # Query the archived assignments to get all of the currently archived ones
        logger.info("Querying target features")
        archived_assignments = target_fl.query(out_fields=field_mappings["GlobalID"])
        # Create a list of GlobalIDs - These should be unique
        global_ids = [feature.attributes[field_mappings["GlobalID"]] for feature in archived_assignments.features]
        # Iterate through the the assignments returned and only add those that don't exist in the Feature Layer
        # that is storing the archived ones
        assignments_to_copy = []
        for assignment in current_assignments.features:
            if assignment.attributes["GlobalID"] not in global_ids:
                assignments_to_copy.append(assignment)
            # Create a new list to store the updated feature-dictionaries
        assignments_to_submit = []
        # Loop over all assignments that we want to add,
        for assignment in assignments_to_copy:
            # map the field names appropriately
            assignment_attributes = {}
            for key, value in field_mappings.items():
                assignment_attributes[value] = assignment.attributes[key]
            # create the new feature object to send to server
            assignments_to_submit.append(arcgis.features.Feature(geometry=assignment.geometry, attributes=assignment_attributes))
        logger.info("Copying assignments...")
        response = target_fl.edit_features(adds=arcgis.features.FeatureSet(assignments_to_submit))
        logger.info(response)
        logger.info("Completed")


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
    parser.add_argument('-targetFL', dest='targetFL', help="The feature layer to copy the assignments to",
                        required=True)
    parser.add_argument('-configFile', dest="configFile", help="The json configuration file to use", required=True)
    parser.add_argument('-logFile', dest='logFile', help="The log file to write to", required=True)
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
