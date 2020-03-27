# -*- coding: UTF-8 -*-
"""
   Copyright 2020 Esri

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
import tempfile
import traceback
import sys
import arcgis
from arcgis.apps import workforce
from arcgis.gis import GIS


def initialize_logging(log_file=None):
    """
    Setup logging
    :param log_file: (string) The file to log to
    :return: (Logger) a logging instance
    """
    # initialize logging
    formatter = logging.Formatter(
        "[%(asctime)s] [%(filename)30s:%(lineno)4s - %(funcName)30s()][%(threadName)5s] [%(name)10.10s] [%(levelname)8s] %(message)s")
    # Grab the root logger
    logger = logging.getLogger()
    # Set the root logger logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.DEBUG)
    # Create a handler to print to the console
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    # Create a handler to log to the specified file
    if log_file:
        rh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10485760)
        rh.setFormatter(formatter)
        rh.setLevel(logging.DEBUG)
        logger.addHandler(rh)
    # Add the handlers to the root logger
    logger.addHandler(sh)
    return logger


def main(arguments):
    # initialize logging
    logger = initialize_logging(arguments.log_file)

    # Create the GIS
    logger.info("Authenticating...")

    # First step is to authenticate
    gis = GIS(arguments.org_url,
              username=arguments.username,
              password=arguments.password,
              verify_cert=not arguments.skip_ssl_verification)

    # Get the target feature layer
    target_fl = arcgis.features.FeatureLayer(arguments.target_fl, gis)

    # Get the project info
    item = gis.content.get(arguments.project_id)
    project = workforce.Project(item)

    # Open the field mappings config file
    logging.getLogger().info("Reading field mappings...")
    with open(arguments.config_file, 'r') as f:
        field_mappings = json.load(f)
    logging.getLogger().info("Validating field mappings...")

    # Query the source to get the features specified by the query string
    logger.info("Querying source features...")
    current_assignments = project.assignments.search(where=arguments.where)

    # Query the archived assignments to get all of the currently archived ones
    logger.info("Querying target features")
    archived_assignments = target_fl.query(out_fields=field_mappings[project._assignment_schema.global_id])

    # Create a list of GlobalIDs - These should be unique
    global_ids = [feature.attributes[field_mappings[project._assignment_schema.global_id]] for feature in archived_assignments.features]

    # Iterate through the the assignments returned and only add those that don't exist in the Feature Layer
    assignments_to_copy = []
    # Updated loop to get the global_id and only copy if it doesn't already exist in global_ids
    for assignment in current_assignments:
        if assignment.global_id not in global_ids:
            assignments_to_copy.append(assignment)

    # Create a new list to store the updated feature-dictionaries
    assignments_to_submit = []
    # Loop over all assignments that we want to add,
    for assignment in assignments_to_copy:
        # map the field names appropriately
        assignment_attributes = {}
        for key, value in field_mappings.items():
            # Updated the feature.attributes to call the correct field mapping items
            assignment_attributes[value] = assignment.feature.attributes[key]
        # create the new feature object to send to server
        assignments_to_submit.append(
            arcgis.features.Feature(geometry=assignment.geometry, attributes=assignment_attributes))
    logger.info("Copying assignments...")
    response = target_fl.edit_features(adds=arcgis.features.FeatureSet(assignments_to_submit))
    logger.info(response)
    if arguments.copy_attachments:
        if target_fl.properties.get("hasAttachments", None):
            logger.info("Copying Attachments...")
            for assignment in assignments_to_copy:
                with tempfile.TemporaryDirectory() as d:
                    attachments = assignment.attachments.download(out_folder=d)
                    if attachments:
                        feature = target_fl.query(where="{} = {}".format(field_mappings[project._assignment_schema.object_id], assignment.object_id)).features[0]
                        for attachment in attachments:
                            target_fl.attachments.add(feature.attributes[target_fl.properties["objectIdField"]], attachment)
        else:
            logger.warning("Attachments not supported on the target layer")
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
    parser.add_argument('-target-fl', dest='target_fl', help="The feature layer to copy the assignments to",
                        required=True)
    parser.add_argument('-config-file', dest="config_file", help="The json configuration file to use", required=True)
    parser.add_argument('-log-file', dest='log_file', help="The log file to write to")
    parser.add_argument('--skip-ssl-verification', dest='skip_ssl_verification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    parser.add_argument('--copy-attachments', dest="copy_attachments", action="store_true", default=False)
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
