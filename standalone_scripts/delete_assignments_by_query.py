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

    This sample deletes assignments from a workforce project based on the supplied query
"""
import argparse
import logging
import logging.handlers
import traceback
import workforcehelpers


def delete_assignments(assignment_fl_url, token, objectIDs, where):
    # Set the required parameters for the request
    params = dict(
        token=token,
        f="json"
    )
    # If we have objectIds, then add them to the parameters as CSVs
    if objectIDs:
        params["objectIds"] = ",".join(objectIDs)
    # if we have a query, then use it
    elif where:
        params["where"] = where
    # if for some reason we have neither, let's just set the query to delete nothing
    else:
        params["where"] = "1=0"  # don't delete anything
    # Build the delete features url
    delete_url = "{}/deleteFeatures".format(assignment_fl_url.rstrip("/"))
    response = workforcehelpers.post(delete_url, params)
    return response


def main(args):
    # Authenticate with AGOL and get the requried token
    logging.getLogger().info("Authenticating...")
    token = workforcehelpers.get_token(args.org_url, args.username, args.password)
    # Get the assignments feature layer url
    logging.getLogger().info("Getting assignment feature layer...")
    assignment_fl_url = workforcehelpers.get_assignments_feature_layer_url(args.org_url, token, args.projectId)
    logging.getLogger().info("Deleting assignments...")
    response = delete_assignments(assignment_fl_url, token, args.objectIDs, args.where)
    logging.getLogger().info(response)
    logging.getLogger().info("Completed")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Delete Assignments to Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-url', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-pid', dest='projectId', help="The id of the project to delete assignments from",
                        required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-where', dest='where', help="The where clause to use", default=None)
    group.add_argument('-objectIDs', dest='objectIDs', help="The objectIds to delete", nargs="+", default=[])
    parser.add_argument('-logFile', dest="logFile", help="The file to log to", required=True)

    args = parser.parse_args()
    workforcehelpers.initialize_logging(args.logFile)
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))