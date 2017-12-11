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


def log_critical_and_raise_exception(message):
    logging.getLogger().critical(message)
    raise Exception(message)


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
    :return:
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
            log_critical_and_raise_exception("Config file is missing: '{}' field mapping".format(field))
    # Check that the provided fields exist in the target feature layer
    for field in field_mappings.values():
        if field not in field_names:
            log_critical_and_raise_exception("Field '{}' is not present in the provided target feature layer".format(field))


def get_completed_assignments(assignment_fl, worker_fl, workers):
    """
    Gets the assignments that have been completed by one of the specified workers
    :param assignment_fl: (string) The FS layer that has the assignments
    :param worker_fl: (string) The FS layer that has the workers
    :param workers: (List<string) The list of worker usernames
    :return: (List<Feature>) The list of assignments
    """
    # Get the workers ids
    if not workers:
        workers = [feature.attributes[get_field_name("userId", worker_fl)] for feature in worker_fl.query().features]

    # Query worker id
    worker_query = "{} in ({})".format(get_field_name("userId", worker_fl),
                                       ",".join(["'{}'".format(w) for w in workers]))
    worker_ids = [w.attributes[get_field_name("OBJECTID", worker_fl)] for w in
                  worker_fl.query(where=worker_query).features]
    if not worker_ids:
        logging.getLogger().info("No assignments completed by specified workers")
        return
    logging.getLogger().info("Querying source features...")
    assignment_query = "{} in ({}) AND {} is not NULL".format(get_field_name("workerId", assignment_fl),
                                                              ",".join(["'{}'".format(w) for w in worker_ids]),
                                                              get_field_name("completedDate", assignment_fl))
    completed_assignments = assignment_fl.query(assignment_query).features
    return completed_assignments


def get_invalid_assignments(assignments, tracks_fl, time_tolerance, distance_tolerance, min_accuracy, assignment_fl):
    """
    Filters the assignment based on time and distance
    :param assignments: (List<Feature>) The assignments to check
    :param tracks_fl: (string) The tracks FS layer
    :param time_tolerance: (int) The tolerance (in minutes) to use when verifying locations
    :param distance_tolerance: (float) The distance (in meters) to use when verifiying locations
    :param min_accuracy: (float) The minimum distance required
    :param assignment_fl: (FeatureLayer) The assignment feature layer
    :return: (List<Feature>) The list of assigments that are invalid
    """
    # Find invalid assignments
    invalid_assignments = []
    for assignment in assignments:
        # The coordinates of the assignment
        start_coords = (assignment.geometry["x"], assignment.geometry["y"])
        # When the assignment was completed
        completion_date = datetime.datetime.utcfromtimestamp(
            int(assignment.attributes[get_field_name("completedDate", assignment_fl)]) / 1000)
        # Add/Subtract some minutes to give a little leeway
        start_date = completion_date - datetime.timedelta(minutes=time_tolerance)
        end_date = completion_date + datetime.timedelta(minutes=time_tolerance)
        # Make a query string to select location by the worker during the time period
        loc_query_string = "{} = '{}' AND {} >= '{}' AND {} <= '{}' AND {} <= {}" \
            .format(get_field_name("Editor", tracks_fl), assignment.attributes[get_field_name("Editor", tracks_fl)],
                    get_field_name("CreationDate", tracks_fl),
                    start_date.strftime('%Y-%m-%d %H:%M:%S'), get_field_name("CreationDate", tracks_fl),
                    end_date.strftime('%Y-%m-%d %H:%M:%S'), get_field_name("Accuracy", tracks_fl),
                    min_accuracy)
        # Query the feature layer
        locations_to_check = tracks_fl.query(where=loc_query_string).features
        # Bool to see if this assignment is valid or not
        is_valid = False
        for location in locations_to_check:
            # Make a list of coordinate pairs to get the distance of
            coords = [(location.geometry["x"], location.geometry["y"])]
            # If we include the accuracy, we need to make four variations (+- the accuracy)
            accuracy = float(location.attributes[get_field_name("Accuracy", tracks_fl)])
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
            if any(distance < distance_tolerance for distance in distances):
                is_valid = True
                break
        # if it's not valid add the OBJECTID to the list of invalid assignment OBJECTIDS
        if not is_valid:
            logging.debug("Location Query: {}".format(loc_query_string))
            invalid_assignments.append(assignment)
    return invalid_assignments


def copy_assignments(assignments, target_fl, field_mappings, assignment_fl):
    """
    Copies the assignments to the target feature service layer
    :param assignments: (List<Feature>) The list of assignments to add
    :param target_fl: (string) The target feature layer to add the assignments to
    :param field_mappings: (dict) The field mappings that convert the original fields to the target fields
    :param assignment_fl: (FeatureLayer) The assignment feature layer
    :return:
    """
    # Query the archived assignments to get all of the currently archived/invalid ones
    logging.getLogger().info("Querying target features")
    archived_assignments = target_fl.query(out_fields=field_mappings["GlobalID"])
    # Create a list of GlobalIDs - These should be unique
    global_ids = [feature.attributes[field_mappings["GlobalID"]] for feature in archived_assignments.features]
    # Iterate through the the assignments returned and only add those that don't exist in the Feature Layer
    # that is storing the archived ones
    assignments_to_copy = []
    for assignment in assignments:
        if assignment.attributes[get_field_name("GlobalID", assignment_fl)] not in global_ids:
            assignments_to_copy.append(assignment)
    # Create a new list to store the updated feature-dictionaries
    assignments_to_submit = []
    # Loop over all assignments that we want to add,
    for assignment in assignments_to_copy:
        # map the field names appropriately
        assignment_attributes = {}
        for key, value in field_mappings.items():
            assignment_attributes[value] = assignment.attributes[get_field_name(key, assignment_fl)]
        # create the new feature object to send to server
        assignments_to_submit.append(
            arcgis.features.Feature(geometry=assignment.geometry, attributes=assignment_attributes))
    if assignments_to_submit:
        logging.getLogger().info("Adding invalid assignments to target Feature Service...")
        response = target_fl.edit_features(adds=arcgis.features.FeatureSet(assignments_to_submit))
        logging.getLogger().info(response)
    else:
        logging.getLogger().info("No invalid completed assignments detected")
    logging.getLogger().info("Completed")


def get_simple_distance(coords1, coords2):
    """
    Calculates the simple distance between two x,y points
    :param coords1: (Tuple) of x and y coordinates
    :param coords2: (Tuple) of x and y coordinates
    :return: (float) The distance between the two points
    """
    return math.sqrt((coords1[0] - coords2[0]) ** 2 + (coords1[1] - coords2[1]) ** 2)


def main(arguments):
    # initialize logger
    logger = initialize_logging(arguments.logFile)
    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = arcgis.gis.GIS(arguments.org_url, username=arguments.username, password=arguments.password, verify_cert=False)

    # Get the project and data
    workforce_project = arcgis.gis.Item(gis, arguments.projectId)
    workforce_project_data = workforce_project.get_data()
    assignment_fl = arcgis.features.FeatureLayer(workforce_project_data["assignments"]["url"], gis)
    tracks_fl = arcgis.features.FeatureLayer(workforce_project_data["tracks"]["url"], gis)
    worker_fl = arcgis.features.FeatureLayer(workforce_project_data["workers"]["url"], gis)
    target_fl = arcgis.features.FeatureLayer(arguments.targetFL, gis)

    # Open the field mappings config file
    logging.getLogger().info("Reading field mappings...")
    with open(arguments.configFile, 'r') as f:
        field_mappings = json.load(f)
        validate_config(target_fl, field_mappings)
        completed_assignments = get_completed_assignments(assignment_fl, worker_fl, arguments.workers)
        invalid_assignments = get_invalid_assignments(completed_assignments, tracks_fl, arguments.timeTol,
                                                      arguments.distTol,
                                                      arguments.minAccuracy, assignment_fl)
        copy_assignments(invalid_assignments, target_fl, field_mappings, assignment_fl)


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
    parser.add_argument('-workers', dest='workers', nargs="+", help="The id of the worker to check")
    parser.add_argument('-timeTol', dest='timeTol',
                        help="The tolerance (in minutes) to check completion date vs location", type=int, default=5)
    parser.add_argument('-distTol', dest='distTol', type=int, default=100,
                        help='The distance tolerance to use (meters- based on SR of Assignments FL)')
    parser.add_argument('-minAccuracy', dest='minAccuracy', default=50,
                        help="The minimum accuracy to use (meters - based on SR of Assignments FL)")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
