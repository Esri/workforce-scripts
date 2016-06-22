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

    This sample copies assignments from one project to another feature service
"""
import argparse
import json
import logging
import logging.handlers
import traceback
import workforcehelpers


def copy_assignments(source_fl_url, target_fl_url, field_mappings, token, where="1=1"):
    """
    This copies assignments (features) from the target feature layer to the source layer, based on the provided field
    mappings and query to select the assignments to copy over.

    The assignments are checked (via GlobalID) to see if they already exist in the target feature layer, if not they
    are then added
    :param source_fl_url: (string) The url to the feature layer to get the assignments from
    :param target_fl_url: (string) The url to the feature layer copy the assignments to
    :param field_mappings: (dictionary) The mapping of the assignment field to the archive fields
    :param token: (string) The token to authenticate with
    :param where: (string) The where clause to use to query
    :return:
    """
    # Query the source to get the features specified by the query string
    logging.getLogger().debug("Querying source features...")
    target_fl_data = workforcehelpers.get_feature_layer(target_fl_url, token)
    current_assignments = workforcehelpers.query_feature_layer(source_fl_url, token, where = where,
                                                               outSR = target_fl_data["extent"]["spatialReference"]["wkid"])["features"]
    # Query the archived assignments to get all of the currently archived ones
    logging.getLogger().debug("Querying target features")
    archived_assignments = workforcehelpers.query_feature_layer(target_fl_url, token, where="1=1", outFields=field_mappings["GlobalID"])["features"]
    # Create a list of GlobalIDs - These should be unique
    global_ids = [feature["attributes"][field_mappings["GlobalID"]] for feature in archived_assignments]
    # Iterate through the the assignments returned and only add those that don't exist in the Feature Layer
    # that is storing the archived ones
    logging.getLogger().debug("")
    assignments_to_copy = []
    for assignment in current_assignments:
        if assignment["attributes"]["GlobalID"] not in global_ids:
            assignments_to_copy.append(assignment)
    # Create a new list to store the updated feature-dictionaries
    assignments_to_copy_dict = []
    # Loop over all assignments that we want to add,
    # Map update the field mappings and create a new dictionary object and add it to the list
    for assignment in assignments_to_copy:
        assignment_dict = {'geometry': assignment["geometry"],
                           'attributes': {}}
        for key, value in field_mappings.items():
            assignment_dict["attributes"][value] = assignment["attributes"][key]
        assignments_to_copy_dict.append(assignment_dict)
    # Convert the list of dictionaries to a list of Feature Objects
    logging.getLogger().debug("Copying Assignments...")
    add_url = "{}/addFeatures".format(target_fl_url)
    data = {
        'token': token,
        'f': 'json',
        'features': json.dumps(assignments_to_copy_dict)
    }
    response = workforcehelpers.post(add_url, data)
    logging.getLogger().info(response)


def validate_config(config_dict, target_fl_url, token):
    """
    Checks the configuration mapping
    :param config_dict: (dictionary) The field mappings dictionary to check
    :param target_fl_url: (string) The target feature layer url
    :param token: (string) The token to authenticate with
    :return:
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
    target_fields = workforcehelpers.get_feature_layer(target_fl_url, token)["fields"]
    field_names = [field["name"] for field in target_fields]
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


def main(args):
    """
    The main sequence of steps
    :param args: The argparse args
    :return:
    """
    # Authenticate
    logging.getLogger().info("Authenticating...")
    token = workforcehelpers.get_token(args.org_url, args.username, args.password)
    # Get the assignments feature layer
    logging.getLogger().info("Getting assignments feature layer...")
    assignment_fl_url = workforcehelpers.get_assignments_feature_layer_url(args.org_url, token, args.projectId)
    # Get the target feature layer
    logging.getLogger().info("Getting target feature layer...")
    target_fl_url = args.targetFL
    # Open the field mappings config file
    logging.getLogger().info("Reading field mappings...")
    with open(args.configFile, 'r') as f:
        field_mappings = json.load(f)
    logging.getLogger().info("Validating field mappings...")
    if validate_config(field_mappings, target_fl_url, token):
        # Copy the assignments
        copy_assignments(assignment_fl_url, target_fl_url, field_mappings, token)
        logging.getLogger().info("Completed")
    else:
        logging.getLogger().critical("Invalid field mappings detected")


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
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
