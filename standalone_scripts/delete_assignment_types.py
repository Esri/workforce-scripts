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

   This sample deletes all assignment types (Will mess up your assignments if you have any)
"""

import argparse
import json
import logging
import logging.handlers
import traceback
import workforcehelpers


def delete_assignment_types(org_url, token, projectId):
    """
    Adds the assignments to project
    :param org_url: (string) The organizational url to use
    :param token: (string) The token to authenticate with
    :param projectId: (string) The project Id
    :return: The json response of the REST API Call
    """
    logger = logging.getLogger()
    # get the assignments feature layer
    assignments_url = workforcehelpers.get_assignments_feature_layer_url(org_url, token, projectId)
    data = {
        'token': token,
        'f': 'json'
    }
    # get the json
    assignment_fl = workforcehelpers.get(assignments_url, params=data)
    for field in assignment_fl["fields"]:
        if field["name"] == "assignmentType":
            field["domain"]["codedValues"] = []
            break
    # clear out lastEditDate (otherwise ArcGIS online throws an error about it)
    if "editingInfo" in assignment_fl and "lastEditDate" in assignment_fl["editingInfo"]:
        del assignment_fl["editingInfo"]["lastEditDate"]
    # clear out hasGeometry properties before submitting (known issue with FS)
    if "hasGeometryProperties" in assignment_fl:
        del assignment_fl["hasGeometryProperties"]
    # need to use the admin url to update a service definition
    index = assignments_url.index("/services/")
    update_definition_url = assignments_url[0:index] + "/admin" + assignments_url[index:] + "/updateDefinition"
    data = {
        'token': token,
        'f': 'json',
        'updateDefinition': json.dumps(assignment_fl)
    }
    logger.debug("Adding Assignment types...")
    # send the data
    response = workforcehelpers.post(update_definition_url, data)
    return response


def main(args):
    logger = logging.getLogger()
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    logger.info("Deleting assignment types")
    token = workforcehelpers.get_token(args.org_url, args.username, args.password)
    delete_assignment_types(args.org_url, token, args.projectId)
    logger.info("Completed")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Add Assignments to Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-url', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-pid', dest='projectId', help="The id of the project to add assignments to", required=True)
    parser.add_argument('-logFile', dest='logFile', help='The log file to use', required=True)
    args = parser.parse_args()
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))