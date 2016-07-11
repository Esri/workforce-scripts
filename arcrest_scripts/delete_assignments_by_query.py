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

    This sample deletes assignments from a workforce project based on the supplied query
"""
import argparse
import logging
import logging.handlers
import traceback
import workforcehelpers


def main(args):
    logging.getLogger().info("Authenticating...")
    shh = workforcehelpers.get_security_handler(args)
    logging.getLogger().info("Getting assignment feature layer...")
    assignment_fl = workforcehelpers.get_assignments_feature_layer(shh, args.projectId)
    logging.getLogger().info("Deleting assignments...")
    response = assignment_fl.deleteFeatures(objectIds=",".join(args.objectIDs), where=args.where)
    logging.getLogger().info(response)
    logging.getLogger().info("Completed")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Delete Assignments to Workforce Project")
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