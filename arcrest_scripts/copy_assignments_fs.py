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
import arcrest
import argparse
import json
import logging
import logging.handlers
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


def main(args):
    """
    The main sequence of steps
    :param args: The argparse args
    :return:
    """
    # Authenticate
    logging.getLogger().info("Authenticating...")
    shh = workforcehelpers.get_security_handler(args)
    # Get the assignments feature layer
    logging.getLogger().info("Getting assignments feature layer...")
    assignment_fl = workforcehelpers.get_assignments_feature_layer(shh, args.projectId)
    # Get the target feature layer
    logging.getLogger().info("Getting target feature layer...")
    target_fl = arcrest.agol.FeatureLayer(args.targetFL, shh.securityhandler)
    # Check that the layer was loaded properly
    if target_fl.hasError():
        logging.getLogger().critical("Error with target feature layer: {}".format(target_fl.error))
        return
    # Open the field mappings config file
    logging.getLogger().info("Reading field mappings...")
    with open(args.configFile, 'r') as f:
        field_mappings = json.load(f)
    logging.getLogger().info("Validating field mappings...")
    if validate_config(field_mappings, target_fl):
        # Copy the assignments
        copy_assignments(assignment_fl, target_fl, field_mappings)
        logging.getLogger().info("Completed")
    else:
        logging.getLogger().critical("Invalid field mappings detected")


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
    args = parser.parse_args()
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
