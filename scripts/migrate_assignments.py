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

    This sample migrates assignment data from v1 projects to v2 projects
"""

import argparse
import logging
import logging.handlers
import tempfile
import sys
import traceback
from arcgis.gis import GIS
from arcgis.apps import workforce
from arcgis.features import Feature, FeatureSet


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


def get_assignment_type_global_id(assignment_types, assignment_type_name):
    for at in assignment_types:
        if at.name == assignment_type_name:
            return at.global_id


def get_worker_global_id(old_workers, new_worker_manager, worker_object_id):
    for worker in old_workers:
        if worker.object_id == worker_object_id:
            return new_worker_manager.get(user_id=worker.user_id).global_id


def get_dispatcher_global_id(old_dispatchers, new_dispatcher_manager, dispatcher_object_id):
    for dispatcher in old_dispatchers:
        if dispatcher.object_id == dispatcher_object_id:
            return new_dispatcher_manager.get(user_id=dispatcher.user_id).global_id
    return new_dispatcher_manager.search()[0].global_id


def add_custom_fields(old_layer, new_layer):
    custom_fields = []
    new_fields = new_layer.properties["fields"]
    old_fields = old_layer.properties["fields"]
    types = new_layer.properties["types"]
    for old_field in old_fields:
        if not any(old_field["name"].lower() == new_field["name"].lower() for new_field in new_fields):
            if old_field["name"] != "assignmentRead":
                custom_fields.append(old_field)
                for index, type in enumerate(types):
                    templates = type["templates"]
                    for index, template in enumerate(templates):
                        template["prototype"]["attributes"][old_field["name"]] = None
                if len(types) > 0:
                    new_layer.manager.update_definition({"types": types})
    new_layer.manager.add_to_definition({"fields": custom_fields})
    return custom_fields


def main(arguments):  # noqa: C901
    # Initialize logging
    logger = initialize_logging(arguments.log_file)

    # Create the GIS
    logger.info("Authenticating...")

    # First step is to get authenticate and get a valid token
    gis = GIS(arguments.org_url,
              username=arguments.username,
              password=arguments.password,
              verify_cert=not arguments.skip_ssl_verification)

    # Get the old workforce project
    item = gis.content.get(arguments.classic_project_id)
    project = workforce.Project(item)
    try:
        if project._is_v2_project:
            raise Exception("The first project provided is a v2 project. Please migrate assignment data from v1 projects")
    except AttributeError:
        raise Exception("Cannot find the attribute is v2 project. Are you sure you have the API version 1.8.3 or greater installed? "
                        "Check with `arcgis.__version__` in your Python console")

    # Get new workforce project
    v2_project = workforce.Project(gis.content.get(arguments.new_project_id))
    if not v2_project._is_v2_project:
        raise Exception("The second project provided is a v1 project. Please migrate assignment data to v2 projects")

    # validate correct assignment types are present
    existing_assignment_types = project.assignment_types.search()
    for assignment_type in existing_assignment_types:
        if not v2_project.assignment_types.get(name=assignment_type.name):
            raise Exception("One of your assignment types in your classic project is not in your offline project")

    # validate correct workers are present
    for worker in project.workers.search():
        if not v2_project.workers.get(user_id=worker.user_id):
            raise Exception("One of your workers in your classic project is not in your offline project")

    # Migrate Assignments
    logger.info("Migrating assignments")
    assignment_ghost = False

    # Get Existing Assignments
    existing_assignments = project.assignments_layer.query(where=arguments.where, return_all_records=True).features
    assignments_to_add = []
    layer = v2_project.assignments_layer

    # Set Custom Fields for Assignments and Templates
    custom_fields = add_custom_fields(project.assignments_layer, layer)

    # Prepare Assignments to be Added
    for assignment in existing_assignments:
        if assignment.attributes[project._assignment_schema.assignment_type]:

            # set attributes in case they are empty
            assignment_location = (str(assignment.geometry["x"]) + " " + str(assignment.geometry["y"])) if \
                assignment.attributes[project._assignment_schema.location] is None else \
                assignment.attributes[project._assignment_schema.location]
            assignment_status = 0 if assignment.attributes[project._assignment_schema.status] is None else \
                assignment.attributes[project._assignment_schema.status]
            assignment_priority = 0 if assignment.attributes[project._assignment_schema.priority] is None else \
                assignment.attributes[project._assignment_schema.priority]

            # get AT name based on code stored
            assignment_type_name = ""
            for at in existing_assignment_types:
                if at.code == assignment.attributes[project._assignment_schema.assignment_type]:
                    assignment_type_name = at.name
                    break

            # Set attributes
            attributes = {v2_project._assignment_schema.status: assignment_status,
                          v2_project._assignment_schema.notes: assignment.attributes[project._assignment_schema.notes],
                          v2_project._assignment_schema.priority: assignment_priority,
                          v2_project._assignment_schema.assignment_type:
                              get_assignment_type_global_id(v2_project.assignment_types.search(), assignment_type_name),
                          v2_project._assignment_schema.work_order_id: assignment.attributes[project._assignment_schema.work_order_id],
                          v2_project._assignment_schema.due_date: assignment.attributes[project._assignment_schema.due_date],
                          v2_project._assignment_schema.description: assignment.attributes[project._assignment_schema.description],
                          v2_project._assignment_schema.worker_id:
                              get_worker_global_id(project.workers.search(), v2_project.workers, assignment.attributes[project._assignment_schema.worker_id]),
                          v2_project._assignment_schema.location: assignment_location,
                          v2_project._assignment_schema.declined_comment: assignment.attributes[project._assignment_schema.declined_comment],
                          v2_project._assignment_schema.assigned_date: assignment.attributes[project._assignment_schema.assigned_date],
                          v2_project._assignment_schema.in_progress_date: assignment.attributes[project._assignment_schema.in_progress_date],
                          v2_project._assignment_schema.completed_date: assignment.attributes[project._assignment_schema.completed_date],
                          v2_project._assignment_schema.declined_date: assignment.attributes[project._assignment_schema.declined_date],
                          v2_project._assignment_schema.paused_date: assignment.attributes[project._assignment_schema.paused_date],
                          v2_project._assignment_schema.dispatcher_id:
                              get_dispatcher_global_id(project.dispatchers.search(), v2_project.dispatchers,
                                                       assignment.attributes[project._assignment_schema.dispatcher_id]),
                          v2_project._assignment_schema.global_id: assignment.attributes[project._assignment_schema.global_id],
                          v2_project._assignment_schema.object_id: assignment.attributes[project._assignment_schema.object_id]}

            # Add Custom Field Values
            for field in custom_fields:
                attributes[field["name"]] = assignment.attributes[field["name"]]
            feature = Feature(geometry=assignment.geometry, attributes=attributes)
            assignments_to_add.append(feature)
        else:
            logger.info("One assignment's migration skipped - does not have an assignment type")
            assignment_ghost = True

    # Add Assignments
    layer.edit_features(adds=FeatureSet(assignments_to_add), use_global_ids=True)
    new_assignments = v2_project.assignments_layer.query("1=1", return_all_records=True).features
    # skip validation if there's a ghost
    if (len(new_assignments) == len(existing_assignments)) or assignment_ghost:
        logger.info("Assignments successfully migrated")
    else:
        raise Exception("Assignments not migrated successfully. Unknown error")

    # Migrate Attachments
    logger.info("Migrating Attachments")
    for assignment in existing_assignments:
        object_id = assignment.attributes[project._assignment_schema.object_id]
        new_assignment_object_id = v2_project.assignments.get(global_id=assignment.attributes[project._assignment_schema.global_id]).object_id
        if len(project.assignments_layer.attachments.get_list(object_id)) > 0:
            try:
                with tempfile.TemporaryDirectory() as dirpath:
                    paths = project.assignments_layer.attachments.download(oid=object_id, save_path=dirpath)
                    for path in paths:
                        v2_project.assignments_layer.attachments.add(oid=new_assignment_object_id, file_path=path)
            except Exception as e:
                logger.info(e)
                logger.info("Skipping migration of this attachment. It did not download successfully")
    if len(project.assignments_layer.attachments.search("1=1")) == len(
            v2_project.assignments_layer.attachments.search("1=1")):
        logger.info("Attachments successfully migrated")
    else:
        logger.info("Not all of your attachments migrated successfully. Continuing with migration")
    logger.info("Script Completed")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Migrate Version 1 Project assignment data to Version 2")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-org', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-classic-project-id', dest='classic_project_id', help="The id of the classic project whose assignments you want to migrate",
                        required=True)
    parser.add_argument('-new-project-id', dest='new_project_id', help="The id of the v2 project who you want to have the new assignments", required=True)
    parser.add_argument('-where', dest='where',
                        help="The where clause to determine what assignments to migrate. "
                             "Defaults to status IN (O, 1, 2, 4, 5) - completed and canceled assignments will not be migrated by default",
                        default="status IN (0, 1, 2, 4, 5)")
    parser.add_argument('-log-file', dest='log_file', help='The log file to use')
    parser.add_argument('--skip-ssl-verification', dest='skip_ssl_verification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
