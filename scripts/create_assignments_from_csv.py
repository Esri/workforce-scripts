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

   This sample creates assignments from CSV files
"""

import argparse
import csv
import logging
import logging.handlers
import traceback
import sys
import arrow
import dateutil
from arcgis.apps import workforce
from arcgis.gis import GIS


def log_critical_and_raise_exception(message):
    logging.getLogger().critical(message)
    raise Exception(message)


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


def main(arguments):
    # initialize logging
    logger = initialize_logging(arguments.logFile)
    # Create the GIS
    logger.info("Authenticating...")
    # First step is to get authenticate and get a valid token
    gis = GIS(arguments.org_url, username=arguments.username, password=arguments.password,
              verify_cert= not arguments.skipSSLVerification)
    # Get the project and data
    item = gis.content.get(arguments.projectId)
    project = workforce.Project(item)
    dispatcher = project.dispatchers.search(where="userId='{}'".format(args.username))
    if not dispatcher:
        log_critical_and_raise_exception("{} is not a dispatcher".format(args.username))
    # Read the csv file
    logger.info("Reading CSV file: {}...".format(arguments.csvFile))
    assignments_in_csv = []
    with open(arguments.csvFile, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            assignments_in_csv.append(row)
    assignment_types = project.assignment_types.search()
    assignment_type_dict = {}
    for assignment_type in assignment_types:
        assignment_type_dict[assignment_type.name] = assignment_type
    assignments_to_add = []
    for assignment in assignments_in_csv:
        assignment_to_add = workforce.Assignment(project)
        # Create the geometry
        geometry = dict(x=float(assignment[args.xField]),
                        y=float(assignment[args.yField]),
                        spatialReference=dict(
                            wkid=int(args.wkid)))
        assignment_to_add.geometry = geometry

        # Determine the assignment due date, and if no time is provided, make the due date all day
        if args.dueDateField and assignment[args.dueDateField]:
            d = arrow.Arrow.strptime(assignment[args.dueDateField], args.dateFormat).replace(
            tzinfo=dateutil.tz.gettz(args.timezone))
            if d.datetime.second == 0 and d.datetime.hour == 0 and d.datetime.minute == 0:
                d = d.replace(hour=23, minute=59, second=59)
            # Convert date to UTC time
            assignment_to_add.due_date = d.to('utc').datetime

        assignment_to_add.assignment_type = assignment_type_dict[assignment[args.assignmentTypeField]]
        # Add location  of assignment from CSV
        assignment_to_add.location = assignment[args.locationField]
        # Add statement to determine if assignment is assigned or not
        if args.workerField and assignment[args.workerField]:
            assignment_to_add.status = "assigned"
        else:
            assignment_to_add.status = "unassigned"
        # Add assignment date and convert the date to UTC from what the API returns
        assignment_to_add.assigned_date = arrow.now().to('utc').datetime

        # Determine who dispatched the assignment
        dispatchers = project.dispatchers.search()
        dispatchers_dict = {}
        for dispatcher in dispatchers:
            dispatchers_dict[dispatcher.user_id] = dispatcher
        if args.dispatcherIdField and assignment[args.dispatcherIdField]:
            assignment_to_add.dispatcher = dispatchers_dict[args.dispatcherIdField]
        else:
            assignment_to_add.dispatcher = dispatcher

        # Define workers and determine which have assignments from the CSV
        workers = project.workers.search()
        workers_dict = {}
        for worker in workers:
            workers_dict[worker.user_id] = worker
        if args.workerField and assignment[args.workerField]:
            assignment_to_add.worker = workers_dict[assignment[args.workerField]]
        else:
            assignment_to_add.worker = worker

        # Add all assignments to the list created
        assignments_to_add.append(assignment_to_add)

    # Batch add all assignments to the project
    project.assignments.batch_add(assignments_to_add)
    logger.info("Complete")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Add Assignments to Workforce Project")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-url', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-pid', dest='projectId', help="The id of the project to add assignments to", required=True)
    parser.add_argument('-xField', dest='xField', help="The field that contains the x SHAPE information", required=True)
    parser.add_argument('-yField', dest='yField', help="The field that contains the y SHAPE information", required=True)
    parser.add_argument('-assignmentTypeField', dest='assignmentTypeField',
                        help="The field that contains the assignmentType", required=True)
    parser.add_argument('-locationField', dest='locationField',
                        help="The field that contains the location", required=True)
    parser.add_argument('-dispatcherIdField', dest='dispatcherIdField',
                        help="The field that contains the dispatcherId")
    parser.add_argument('-descriptionField', dest='descriptionField', help="The field that contains the description")
    parser.add_argument('-priorityField', dest='priorityField', help="The field that contains the priority")
    parser.add_argument('-workOrderIdField', dest='workOrderIdField', help="The field that contains the workOrderId")
    parser.add_argument('-dueDateField', dest='dueDateField', help="The field that contains the dispatcherId")
    parser.add_argument('-workerField', dest='workerField', help="The field that contains the workers username")
    parser.add_argument('-attachmentFileField', dest='attachmentFileField',
                        help="The field that contains the file path to the attachment to upload")
    parser.add_argument('-dateFormat', dest='dateFormat', default="%m/%d/%Y %H:%M:%S",
                        help="The format to use for the date (eg. '%m/%d/%Y %H:%M:%S')")
    parser.add_argument('-timezone', dest='timezone', default="UTC", help="The timezone for the assignments")
    parser.add_argument('-csvFile', dest='csvFile', help="The path/name of the csv file to read")
    parser.add_argument('-wkid', dest='wkid', help='The wkid that the x,y values are use', type=int, default=4326)
    parser.add_argument('-logFile', dest='logFile', help='The log file to use', required=True)
    parser.add_argument('--skipSSL', dest='skipSSLVerification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
