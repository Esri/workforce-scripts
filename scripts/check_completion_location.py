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

    This sample copies assignments from one project to another feature service if the assignments
    were not completed properly
"""
import argparse
import datetime
import json
import logging
import logging.handlers
import math
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


def get_simple_distance(coords1, coords2):
    """
    Calculates the simple distance between two x,y points
    :param coords1: (Tuple) of x and y coordinates
    :param coords2: (Tuple) of x and y coordinates
    :return: (float) The distance between the two points
    """
    return math.sqrt((coords1[0] - coords2[0]) ** 2 + (coords1[1] - coords2[1]) ** 2)


def get_completed_assignments(project, workers):
    """
    Get's the completed assignments
    :param project: (Project) The project to use
    :param workers: (List<String>) The list of worker usernames to get completed assignments for
    :return: List<Assignment> The list of completed assignments
    """
    if not workers:
        workers = project.workers.search()

    worker_query = "{} in ({})".format(project._worker_schema.user_id,
                                       ",".join(["'{}'".format(w) for w in workers]))
    worker_ids = [w.object_id for w in
                  project.workers.search(where=worker_query)]
    if not worker_ids:
        logging.getLogger().info("No assignments completed by specified workers")
        return []
    logging.getLogger().info("Querying source features...")
    assignment_query = "{} in ({}) AND {} is not NULL".format(project._assignment_schema.worker_id,
                                                              ",".join(["'{}'".format(w) for w in worker_ids]),
                                                              project._assignment_schema.completed_date)
    completed_assignments = project.assignments.search(assignment_query)
    return completed_assignments


def copy_assignments(project, assignments, target_fl, field_mappings):
    """
    Copies assignments from the project to another feature layer
    :param project: (Project) The project to copy assignments from
    :param assignments: (List<Assignment>) The list of assignments to copy
    :param target_fl: (Featurelayer) The feature layer to copy the assignments to
    :param field_mappings: (Dict) The dictionary containing the field mappings between the project and target layer
    :return:
    """
    # Query the archived assignments to get all of the currently archived/invalid ones
    logging.getLogger().info("Querying target features")
    archived_assignments = target_fl.query(out_fields=field_mappings[project._assignment_schema.global_id])
    # Create a list of GlobalIDs - These should be unique
    global_ids = [feature.attributes[field_mappings[project._assignment_schema.global_id]] for feature in archived_assignments.features]
    # Iterate through the the assignments returned and only add those that don't exist in the Feature Layer
    # that is storing the archived ones
    assignments_to_copy = []
    for assignment in assignments:
        if assignment.global_id not in global_ids:
            assignments_to_copy.append(assignment)
    # Create a new list to store the updated feature-dictionaries
    assignments_to_submit = []
    # Loop over all assignments that we want to add,
    for assignment in assignments_to_copy:
        # map the field names appropriately
        assignment_attributes = {}
        for key, value in field_mappings.items():
            assignment_attributes[value] = assignment.feature.attributes[key]
        # create the new feature object to send to server
        assignments_to_submit.append(
            arcgis.features.Feature(geometry=assignment.geometry, attributes=assignment_attributes))
    if assignments_to_submit:
        logging.getLogger().info("Adding invalid assignments to target Feature Service...")
        response = target_fl.edit_features(adds=assignments_to_submit)
        logging.getLogger().info(response)
    else:
        logging.getLogger().info("No invalid completed assignments detected")
    logging.getLogger().info("Completed")


def get_invalid_assignments(project, time_tolerance, dist_tolerance, min_accuracy, workers):
    """
    Finds all invalid assignments completed by the specified workers
    :param project: (Project) The workforce project containing the assignments
    :param time_tolerance: (int) The time tolerance to use when evaluating assignments
    :param dist_tolerance: (int) The distance tolerance to use when evaluating assignments
    :param min_accuracy: (int) The minimum accuracy to consider
    :param workers: (List<String>) The list of worker username to consider
    :return:
    """
    completed_assignments = get_completed_assignments(project, workers)
    # Find invalid assignments
    invalid_assignments = []
    # Bug in the Workforce module at 1.4.1 causes accuracy to not be an available property on the schema
    if "Accuracy" in [field["name"] for field in project.tracks_layer.properties.fields]:
        accuracy_field = "Accuracy"
    else:
        accuracy_field = "accuracy"
    for assignment in completed_assignments:
        # The coordinates of the assignment
        start_coords = (assignment.geometry["x"], assignment.geometry["y"])
        # When the assignment was completed
        completion_date = assignment.completed_date
        # Add/Subtract some minutes to give a little leeway
        start_date = completion_date - datetime.timedelta(minutes=time_tolerance)
        end_date = completion_date + datetime.timedelta(minutes=time_tolerance)
        # Make a query string to select location by the worker during the time period
        loc_query_string = "{} = '{}' AND {} >= '{}' AND {} <= '{}' AND {} <= {}" \
            .format(project._track_schema.editor, assignment.editor,
                    project._track_schema.creation_date,
                    start_date.strftime('%Y-%m-%d %H:%M:%S'), project._track_schema.creation_date,
                    end_date.strftime('%Y-%m-%d %H:%M:%S'), accuracy_field,
                    min_accuracy)
        # Query the feature layer
        locations_to_check = project.tracks.search(where=loc_query_string)
        # Bool to see if this assignment is valid or not
        is_valid = False
        for location in locations_to_check:
            # Make a list of coordinate pairs to get the distance of
            coords = [(location.geometry["x"], location.geometry["y"])]
            accuracy = float(location.feature.attributes[accuracy_field])
            # If we include the accuracy, we need to make four variations (+- the accuracy)
            coords.append((location.geometry["x"] + accuracy,
                           location.geometry["y"] + accuracy))
            coords.append((location.geometry["x"] + accuracy,
                           location.geometry["y"] - accuracy))
            coords.append((location.geometry["x"] - accuracy,
                           location.geometry["y"] + accuracy))
            coords.append((location.geometry["x"] - accuracy,
                           location.geometry["y"] - accuracy))
            distances = [get_simple_distance(start_coords, coordinates) for coordinates in coords]
            # if any of the distances is less than the threshold then this assignment is valid
            if any(distance < dist_tolerance for distance in distances):
                is_valid = True
                break
        if not is_valid:
            logging.debug("Location Query: {}".format(loc_query_string))
            invalid_assignments.append(assignment)
    return invalid_assignments


def main(arguments):
    # initialize logger
    logger = initialize_logging(arguments.log_file)

    # Create the GIS
    logger.info("Authenticating...")

    # First step is to get authenticate and get a valid token
    gis = GIS(arguments.org_url,
              username=arguments.username,
              password=arguments.password,
              verify_cert=not arguments.skip_ssl_verification)

    # Get the project
    item = gis.content.get(arguments.project_id)
    project = workforce.Project(item)
    invalid_assignments = get_invalid_assignments(project,
                                                  arguments.time_tolerance,
                                                  arguments.distance_tolerance,
                                                  arguments.min_accuracy,
                                                  arguments.workers)

    with open(arguments.config_file, 'r') as f:
        field_mappings = json.load(f)
    target_fl = arcgis.features.FeatureLayer(arguments.target_fl, gis)
    # Check if layer exists
    try:
        _ = target_fl.properties
    except Exception as e:
        logger.info(e)
        logger.info("Layer could not be found based on given input. Please check your parameters again. Exiting the script")
        sys.exit(0)
    copy_assignments(project, invalid_assignments, target_fl, field_mappings)


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
    parser.add_argument('-workers', dest='workers', nargs="+", help="The id of the worker to check")
    parser.add_argument('-time-tolerance', dest='time_tolerance',
                        help="The tolerance (in minutes) to check completion date vs location", type=int, default=5)
    parser.add_argument('-distance-tolerance', dest='distance_tolerance', type=int, default=100,
                        help='The distance tolerance to use (meters- based on SR of Assignments FL)')
    parser.add_argument('-min-accuracy', dest='min_accuracy', default=50,
                        help="The minimum accuracy to use (meters - based on SR of Assignments FL)")
    parser.add_argument('--skip-ssl-verification',
                        dest='skip_ssl_verification',
                        action='store_true',
                        help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
