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

    This sample deletes assignments from a workforce project based on the supplied query
"""
import argparse
import logging
import logging.handlers
import traceback
import sys
from arcgis.apps import workforce
from arcgis.gis import GIS


def main(arguments):
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
    rh = logging.handlers.RotatingFileHandler(arguments.logFile, mode='a', maxBytes=10485760)
    rh.setFormatter(formatter)
    rh.setLevel(logging.DEBUG)
    # Add the handlers to the root logger
    logger.addHandler(sh)
    logger.addHandler(rh)

    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = GIS(arguments.org_url, username=arguments.username, password=arguments.password,
              verify_cert= not arguments.skipSSLVerification)

    # Get the project and data
    item = gis.content.get(arguments.projectId)
    project = workforce.Project(item)

    # Need to add in a call to the assignment_fl in order to avoid bogging down the server with large assignment calls
    project.assignments_layer.delete_features(where=arguments.where)

    logger.info("Complete")


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
    group.add_argument('-where', dest='where', help="The where clause to use", default="1=1")
    group.add_argument('-objectIDs', dest='objectIDs', help="The objectIds to delete", nargs="+", default=[])
    parser.add_argument('-logFile', dest="logFile", help="The file to log to", required=True)
    parser.add_argument('--skipSSL', dest='skipSSLVerification', action='store_true',
                        help="Verify the SSL Certificate of the server")

    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
