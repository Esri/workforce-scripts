"""
    This sample copies assignments from one project to another feature service
"""
import arcrest
import argparse
import datetime
import json
import logging
import logging.handlers
import math
import traceback
import workforcehelpers


def copy_assignments(source_fl, target_fl, field_mappings, where="1=1"):
    """
    This copies assignments (features) from the target feature layer to the source layer, based on the provided field
    mappings and query to select the assignments to copy over.

    The assignments are checked (via GlobalID) to see if they already exist in the target feature layer, if not they
    are then added
    :param source_fl: (ArcREST Feature Layer Object) The layer to get the assignments from
    :param target_fl: (ArcREST Feature Layer Object) The layer copy the assignments to
    :param field_mappings: (dictionary) The mapping of the assignment field to the archive fields
    :param where: (string) The where clause to use to query
    :return:
    """
    # Query the source to get the features specified by the query string
    logging.getLogger().debug("Querying source features...")
    current_assignments = source_fl.query(where=where, out_fields="*",
                                          outSR=target_fl.extent["spatialReference"]["wkid"]).features
    # Query the archived assignments to get all of the currently archived ones
    logging.getLogger().debug("Querying target features")
    archived_assignments = target_fl.query(where="1=1", out_fields=field_mappings["GlobalID"]).features
    # Create a list of GlobalIDs - These should be unique
    global_ids = [feature.asDictionary["attributes"][field_mappings["GlobalID"]] for feature in archived_assignments]
    # Iterate through the the assignments returned and only add those that don't exist in the Feature Layer
    # that is storing the archived ones
    logging.getLogger().debug("")
    assignments_to_copy = []
    for assignment in current_assignments:
        if assignment.asDictionary["attributes"]["GlobalID"] not in global_ids:
            assignments_to_copy.append(assignment)
    # Create a new list to store the updated feature-dictionaries
    assignments_to_copy_dict = []
    # Loop over all assignments that we want to add,
    # Map update the field mappings and create a new dictionary object and add it to the list
    for assignment in assignments_to_copy:
        assignment_dict = {'geometry': assignment.asDictionary["geometry"],
                           'attributes': {}}
        for key, value in field_mappings.items():
            assignment_dict["attributes"][value] = assignment.asDictionary["attributes"][key]
        assignments_to_copy_dict.append(assignment_dict)
    # Convert the list of dictionaries to a list of Feature Objects
    features = [arcrest.common.general.Feature(x) for x in assignments_to_copy_dict]
    logging.getLogger().debug("Copying Assignments...")
    # Add the features to the feature layer
    response = target_fl.addFeature(features)
    logging.getLogger().info(response)


def validate_config(config_dict, target_fl):
    """
    This checks that the configuration field mappings are valid
    :param config_dict: (dictionary) The field mappings dictionary to check
    :param target_fl: (Feature Layer Object) The target feature layer to check against
    :return: True if valid, False if not
    """
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
    field_names = [field["name"] for field in target_fl.fields]
    # Check that the configuration file is not missing any fields
    for field in fields:
        if field not in config_dict:
            logging.getLogger().critical("Config file is missing: '{}' field mapping".format(field))
            return False
    # Check that the provided fields exist in the target feature layer
    for field in config_dict.values():
        if field not in field_names:
            logging.getLogger().critical("Field '{}' is not present in the provided target feature layer".format(field))
            return False
    return True


def get_worker_id(shh, projectId, worker):
    """
    Get the logged in users dispatcher id
    :param shh: The ArcREST security handler helper
    :param projectId: The projectId to use
    :param worker: The name of the worker to get the id of
    :return: The OBJECTID of the specified dispatcher
    """
    logger = logging.getLogger()
    logger.debug("Getting dispatcher id for: {}...".format(worker))
    worker_fl = workforcehelpers.get_workers_feature_layer(shh, projectId)
    workers = worker_fl.query(where="userId='{}'".format(worker))
    if workers.features:
        return workers.features[0].asDictionary["attributes"]["OBJECTID"]
    else:
        logger.critical("{} is not a worker".format(worker))
        return None


def main(args):
    """
    The main sequence of steps
    :type args: object
    :param args: The argparse args
    :return:
    """
    # Authenticate
    logging.getLogger().info("Authenticating...")
    shh = workforcehelpers.get_security_handler(args)
    # Get the target feature layer
    logging.getLogger().info("Getting target feature layer...")
    target_fl = arcrest.agol.FeatureLayer(args.targetFL, shh.securityhandler)
    # Check that the layer was loaded properly
    if target_fl.hasError():
        logging.getLogger().critical("Error with target feature layer: {}".format(target_fl.error))
        return
    logging.getLogger().info("Getting assignments feature layer...")
    assignment_fl = workforcehelpers.get_assignments_feature_layer(shh, args.projectId)

    # if a specific workers weren't specified, let's use all workers
    if not args.workers:
        features = workforcehelpers.get_workers_feature_layer(shh, args.projectId).query(where="1=1").features
        workers = [feature.asDictionary["attributes"]["userId"] for feature in features]
    else:
        workers = args.workers

    # Open the field mappings config file
    logging.getLogger().info("Reading field mappings...")
    with open(args.configFile, 'r') as f:
        field_mappings = json.load(f)
    # Check the mapping to the target feature service is valid
    logging.getLogger().info("Validating field mappings...")
    if validate_config(field_mappings, target_fl):
        for worker in workers:
            # Get the query string that represents the invalid assignment completions
            query_string = get_invalid_completions(shh, args.projectId, worker,
                                                   args.timeTol, args.distTol, args.minAccuracy)
            # Use that query to copy the assignments to feature service (if they don't already exist)
            copy_assignments(assignment_fl, target_fl, field_mappings, where=query_string)
    else:
        logging.getLogger().critical("Invalid field mappings detected")
        return


def get_invalid_completions(shh, projectId, worker, time_tolerance, distance_tolerance, min_accuracy):
    """
    Generates a query string that represents the assignments that were completed either outside of the
    specified time window or outside of the specified distance
    :param shh: The ArcREST security handler helper
    :param projectID: The projectId to use
    :param worker: (string) The userId (name) of the worker to use
    :param time_tolerance: (int) The number of minutes to use as a tolerance
    :param distance_tolerance: (float or int) The distance tolerance to use
    :param min_accuracy: (int or float) The minimum accuracy to require when querying points
    :return: (string) A query that uses the OBJECTID to identify invalid assignment completions
    """
    logging.getLogger().info("Getting assignments feature layer...")
    assignment_fl = workforcehelpers.get_assignments_feature_layer(shh, projectId)
    # Get the locations feature layer
    logging.getLogger().info("Getting location feature layer...")
    location_fl = workforcehelpers.get_location_feature_layer(shh, projectId)
    # Get workerId
    logging.getLogger().info("Getting workerId for {}".format(worker))
    worker_id = get_worker_id(shh, projectId, worker)
    if not worker_id:
        logging.critical("Invalid worker detected")
        return
    # Get the completed assignments by the specified worker
    completed_assignments = assignment_fl.query(
        where="workerId = {} AND completedDate is not NULL".format(worker_id)).features
    invalid_assignment_oids = []
    # Iterate over the assignments and check to see if they were completed within the specified distance
    for assignment in completed_assignments:
        # The coordinates of the assignment
        start_coords = (assignment.asDictionary["geometry"]["x"], assignment.asDictionary["geometry"]["y"])
        # When the assignment was completed
        completion_date = datetime.datetime.utcfromtimestamp(
            int(assignment.asDictionary["attributes"]["completedDate"])/1000)
        # Add/Subtract some minutes to give a little leeway
        start_date = completion_date - datetime.timedelta(minutes=time_tolerance)
        end_date = completion_date + datetime.timedelta(minutes=time_tolerance)
        # Make a query string to select location by the worker during the time period
        loc_query_string = "Editor = '{}' AND CreationDate >= '{}' AND CreationDate <= '{}' AND Accuracy <= {}"\
            .format(worker, start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    min_accuracy)
        # Query the feature layer
        locations_to_check = location_fl.query(where=loc_query_string).features
        # Bool to see if this assignment is valid or not
        is_valid=False
        for location in locations_to_check:
            # Make a list of coordinate pairs to get the distance of
            coords = []
            # If we include the accuracy, we need to make four variations (+- the accuracy)
            accuracy = float(location.asDictionary["attributes"]["Accuracy"])
            coords.append((location.asDictionary["geometry"]["x"]+accuracy,
                       location.asDictionary["geometry"]["y"]+accuracy))
            coords.append((location.asDictionary["geometry"]["x"]+accuracy,
                       location.asDictionary["geometry"]["y"]-accuracy))
            coords.append((location.asDictionary["geometry"]["x"]-accuracy,
                       location.asDictionary["geometry"]["y"]+accuracy))
            coords.append((location.asDictionary["geometry"]["x"]-accuracy,
                       location.asDictionary["geometry"]["y"]-accuracy))
            distances = [get_simple_distance(start_coords, coordinates) for coordinates in coords]
            # if any of the distances is less than the threshold then this assignment is valid
            if any(distance < distance_tolerance for distance in distances):
                is_valid = True
                break
        # if it's not valid add the OBJECTID to the list of invalid assignment OBJECTIDS
        if not is_valid:
            logging.debug("Location Query: {}".format(loc_query_string))
            invalid_assignment_oids.append(str(assignment.asDictionary["attributes"]["OBJECTID"]))
    if invalid_assignment_oids:
        return "OBJECTID in ({})".format(",".join(invalid_assignment_oids))
    else:
        logging.getLogger().info(
            "All assignments were completed within the specified time and distance. Nothing to copy.")
        return "1=0"


def get_simple_distance(coords1, coords2):
    """
    Calculates the simple distance between two x,y points
    :param coords1: (Tuple) of x and y coordinates
    :param coords2: (Tuple) of x and y coordinates
    :return: (float) The distance between the two points
    """
    return math.sqrt((coords1[0]-coords2[0])**2 + (coords1[1]-coords2[1])**2)


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
    parser.add_argument('-targetFL', dest='targetFL', help="The feature layer to copy the assignments to",
                        required=True)
    parser.add_argument('-configFile', dest="configFile", help="The json configuration file to use", required=True)
    parser.add_argument('-logFile', dest='logFile', help="The log file to write to", required=True)
    parser.add_argument('-workers', dest='workers', nargs="+", help="The id of the worker to check")
    parser.add_argument('-timeTol', dest='timeTol',
                        help="The tolerance (in minutes) to check completion date vs location", type=int, default=5)
    parser.add_argument('-distTol', dest='distTol', type=int, default=100,
                        help='The distance tolerance to use (meters- based on SR of Assignments FL)')
    parser.add_argument('-minAccuracy', dest='minAccuracy', type=int, default=50,
                        help="The minimum accuracy to use (meters - based on SR of Assignments FL)")
    args = parser.parse_args()
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
