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
    
    This sample migrates version 1 projects to version 2
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
import json
import math


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


def _delete_workforce_items(fs_item):
    try:
        fs_item._gis.content.get(fs_item.properties['workforceWorkerWebMapId']).protect(False)
    except Exception:
        pass
    try:
        fs_item._gis.content.get(fs_item.properties['workforceWorkerWebMapId']).delete()
    except Exception:
        pass
    try:
        fs_item._gis.content.get(fs_item.properties['workforceDispatcherWebMapId']).protect(False)
    except Exception:
        pass
    try:
        fs_item._gis.content.get(fs_item.properties['workforceDispatcherWebMapId']).delete()
    except Exception:
        pass
    try:
        fs_item.protect(False)
    except Exception:
        pass
    try:
        fs_item.delete()
    except Exception:
        pass


def cleanup_project(gis, project_name):
    try:
        items = gis.content.search(f'"{project_name}" AND typekeywords:"Workforce Project" AND NOT type:"Web Map"')
        if items:
            _delete_workforce_items(items[0])
    except:
        pass
    try:
        groups = gis.groups.search(f'"{project_name}"')
        for group in groups:
            group.delete()
    except:
        pass
    try:
        folders = gis.users.me.folders
        for folder in folders:
            if folder['title'] == project_name:
                items = gis.content.search(f"ownerfolder:{folder['id']}", max_items=100)
                for item in items:
                    item.protect(False)
                    item.delete()
                gis.content.delete_folder(folder["title"])
    except:
        pass


def get_assignment_type_global_id(assignment_types, assignment_type_name):
    for at in assignment_types:
        if at.name == assignment_type_name:
            return at.global_id
    return None


def get_worker_global_id(workers, worker_object_id):
    for worker in workers:
        if worker.object_id == worker_object_id:
            return worker.global_id


def get_dispatcher_global_id(skip_dispatchers, dispatchers, dispatcher_object_id):
    if not skip_dispatchers:
        for dispatcher in dispatchers:
            if dispatcher.object_id == dispatcher_object_id:
                return dispatcher.global_id
    return None


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


def get_wf_operational_layer(data, layer_id):
    for layer in data["operationalLayers"]:
        if layer["id"] == layer_id:
            return layer


def main(arguments):
    # Initialize logging
    logger = initialize_logging(arguments.log_file)

    # Create the GIS
    logger.info("Authenticating...")

    # First step is to get authenticate and get a valid token
    gis = GIS(arguments.org_url,
              username=arguments.username,
              password=arguments.password,
              verify_cert=not arguments.skip_ssl_verification)

    # Get the workforce project
    item = gis.content.get(arguments.project_id)
    project = workforce.Project(item)
    if project._is_v2_project:
        raise Exception("This is a v2 project. Please migrate v1 projects")
    logger.info(project)
    logger.info("Creating base v2 project...")

    # Create WF Project w given title
    if arguments.title:
        if arguments.title != project.title:
            title = arguments.title
        else:
            raise Exception("Cannot name your project the same as the old one. Please provide a unique name")
    else:
        title = project.title + " Updated"
    v2_project = workforce.create_project(title=title, summary=project.summary, major_version=2)

    # Update thumbnail
    with tempfile.TemporaryDirectory() as dirpath:
        try:
            thumbnail = item.download_thumbnail(save_folder=dirpath)
            v2_project._item.update(thumbnail=thumbnail)
            gis.content.get(v2_project.worker_web_map_id).update(thumbnail=thumbnail)
            gis.content.get(v2_project.dispatcher_web_map_id).update(thumbnail=thumbnail)
        except Exception:
            logger.info("Thumbnail not migrated successfully")

    # Migrate Assignment Types
    logger.info("Migrating assignment types...")
    existing_assignment_types = project.assignment_types.search()
    at_to_add = []

    for assignment_type in existing_assignment_types:
        if assignment_type.name:
            at_to_add.append(workforce.AssignmentType(project=v2_project, name=assignment_type.name))
        else:
            logger.info("Assignment Type migration skipped - does not have a name")

    # Get Assignment Types in migrated project before you potentially add a bad worker / dispatcher
    v2_project.assignment_types.batch_add(at_to_add)
    new_assignment_types = v2_project.assignment_types.search()
    if len(existing_assignment_types) == len(new_assignment_types):
        logger.info("Assignment Types successfully migrated")
    else:
        cleanup_project(gis, title)
        raise Exception("Assignment Types not successfully migrated. Cleaning up new project")

    # Migrate Dispatchers
    if not arguments.skip_dispatchers:
        logger.info("Migrating dispatchers...")
        dispatcher_ghost = False

        # Get Existing Dispatchers
        existing_dispatchers = project.dispatchers.search()
        dispatchers_to_add = []
        layer = v2_project.dispatchers_layer

        # Get Custom Dispatcher Fields and Templates
        custom_fields = add_custom_fields(project.dispatchers_layer, layer)

        # Prepare Dispatchers to be added
        for dispatcher in existing_dispatchers:

            # Validate that there is a user id populated and that the user id isn't yourself (since that was added during project creation). Otherwise, skip adding the dispatcher
            if dispatcher.user_id and dispatcher.user_id != arguments.username:

                # Validate a name exists, otherwise populate with an empty string
                dispatcher_name = dispatcher.user_id if dispatcher.name is None else dispatcher.name

                attributes = {v2_project._dispatcher_schema.name: dispatcher_name,
                              v2_project._dispatcher_schema.contact_number: dispatcher.contact_number,
                              v2_project._dispatcher_schema.user_id: dispatcher.user_id,
                              v2_project._dispatcher_schema.global_id: dispatcher.global_id}

                # Add Custom Field Values
                for field in custom_fields:
                    attributes[field["name"]] = dispatcher._feature.attributes[field["name"]]
                feature = Feature(geometry=dispatcher.geometry, attributes=attributes)
                dispatchers_to_add.append(feature)
            else:
                if not dispatcher.user_id:
                    logger.info(
                        "Dispatcher was skipped from migrating. The dispatcher does not a valid user_id in the layer, or 2. The dispatcher was already added. Please check the original dispatchers layer.")
                    dispatcher_ghost = True
                else:
                    # update info for owner dispatcher
                    v2_dispatcher = v2_project.dispatchers.search()[0]
                    v2_dispatcher.update(contact_number=dispatcher.contact_number, name=dispatcher.name)

        # Add Dispatchers
        layer.edit_features(adds=FeatureSet(dispatchers_to_add), use_global_ids=True)
        # add dispatcher named users to the project's group.
        max_add_per_call = 25
        for i in range(0, math.ceil(len(dispatchers_to_add) / max_add_per_call)):
            v2_project.group.add_users(
                [d.attributes[v2_project._dispatcher_schema.user_id] for d in dispatchers_to_add[i * max_add_per_call:(i * max_add_per_call) + max_add_per_call]])
        new_dispatchers = v2_project.dispatchers_layer.query("1=1", return_all_records=True).features
        if len(existing_dispatchers) == len(new_dispatchers) or dispatcher_ghost:
            logger.info("Dispatchers successfully migrated")
        else:
            raise Exception("Dispatchers not migrated successfully")

    # Migrate Workers
    logger.info("Migrating workers...")
    worker_ghost = False

    # Get Existing Workers
    existing_workers = project.workers_layer.query("1=1", return_all_records=True).features
    workers_to_add = []
    layer = v2_project.workers_layer

    # Get Custom Worker Fields
    custom_fields = add_custom_fields(project.workers_layer, layer)
    # Prepare Workers to be added
    for worker in existing_workers:
        if worker.attributes[project._worker_schema.user_id]:
            worker_name = worker.attributes[project._worker_schema.user_id] if worker.attributes[
                                                                                   project._worker_schema.name] is None else \
            worker.attributes[
                project._worker_schema.name]
            worker_status = 0 if worker.attributes[project._worker_schema.status] is None else worker.attributes[
                project._worker_schema.status]
            attributes = {v2_project._worker_schema.name: worker_name,
                          v2_project._worker_schema.contact_number: worker.attributes[
                              project._worker_schema.contact_number],
                          v2_project._worker_schema.notes: worker.attributes[project._worker_schema.notes],
                          v2_project._worker_schema.status: worker_status,
                          v2_project._worker_schema.title: worker.attributes[project._worker_schema.title],
                          v2_project._worker_schema.user_id: worker.attributes[project._worker_schema.user_id],
                          v2_project._worker_schema.global_id: worker.attributes[project._worker_schema.global_id]}

            # Add Custom Field Values
            for field in custom_fields:
                attributes[field["name"]] = worker.attributes[field["name"]]
            feature = Feature(geometry=worker.geometry, attributes=attributes)
            workers_to_add.append(feature)
        else:
            worker_ghost = True
            logger.info("Worker migration skipped - does not have a user id")

    # Add Workers
    layer.edit_features(adds=FeatureSet(workers_to_add), use_global_ids=True)
    # add worker named users to the project's group.
    max_add_per_call = 25
    for i in range(0, math.ceil(len(workers_to_add) / max_add_per_call)):
        v2_project.group.add_users(
            [w.attributes[v2_project._worker_schema.user_id] for w in
             workers_to_add[i * max_add_per_call:(i * max_add_per_call) + max_add_per_call]])
    new_workers = v2_project.workers_layer.query("1=1", return_all_records=True).features
    if (len(existing_workers) == len(new_workers)) or worker_ghost:
        logger.info("Workers successfully migrated")
    else:
        cleanup_project(gis, title)
        raise Exception("Workers not migrated successfully. Cleaning up new project")

    # Migrate Assignments
    logger.info("Migrating assignments")
    assignment_ghost = False

    # Get Existing Assignments
    existing_assignments = project.assignments_layer.query("1=1", return_all_records=True).features
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
            
            assignment_type_name = ""
            for at in existing_assignment_types:
                if at.code == assignment.attributes[project._assignment_schema.assignment_type]:
                    assignment_type_name = at.name
                    break
            attributes = {v2_project._assignment_schema.status: assignment_status,
                          v2_project._assignment_schema.notes: assignment.attributes[project._assignment_schema.notes],
                          v2_project._assignment_schema.priority: assignment_priority,
                          v2_project._assignment_schema.assignment_type: get_assignment_type_global_id(
                              new_assignment_types, assignment_type_name),
                          v2_project._assignment_schema.work_order_id: assignment.attributes[
                              project._assignment_schema.work_order_id],
                          v2_project._assignment_schema.due_date: assignment.attributes[
                              project._assignment_schema.due_date],
                          v2_project._assignment_schema.description: assignment.attributes[
                              project._assignment_schema.description],
                          v2_project._assignment_schema.worker_id: get_worker_global_id(project.workers.search(),
                                                                                        assignment.attributes[
                                                                                            project._assignment_schema.worker_id]),
                          v2_project._assignment_schema.location: assignment_location,
                          v2_project._assignment_schema.declined_comment: assignment.attributes[
                              project._assignment_schema.declined_comment],
                          v2_project._assignment_schema.assigned_date: assignment.attributes[
                              project._assignment_schema.assigned_date],
                          v2_project._assignment_schema.in_progress_date: assignment.attributes[
                              project._assignment_schema.in_progress_date],
                          v2_project._assignment_schema.completed_date: assignment.attributes[
                              project._assignment_schema.completed_date],
                          v2_project._assignment_schema.declined_date: assignment.attributes[
                              project._assignment_schema.declined_date],
                          v2_project._assignment_schema.paused_date: assignment.attributes[
                              project._assignment_schema.paused_date],
                          v2_project._assignment_schema.dispatcher_id: get_dispatcher_global_id(
                              arguments.skip_dispatchers, project.dispatchers.search(),
                              assignment.attributes[project._assignment_schema.dispatcher_id]),
                          v2_project._assignment_schema.global_id: assignment.attributes[
                              project._assignment_schema.global_id],
                          v2_project._assignment_schema.object_id: assignment.attributes[
                              project._assignment_schema.object_id]}

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
    if (len(new_assignments) == len(existing_assignments)) or assignment_ghost:
        logger.info("Assignments successfully migrated")
    else:
        cleanup_project(gis, title)
        raise Exception("Assignments not migrated successfully. Cleaning up new project")

    # Migrate Attachments
    logger.info("Migrating Attachments")
    for assignment in existing_assignments:
        object_id = assignment.attributes[project._assignment_schema.object_id]
        if len(project.assignments_layer.attachments.get_list(object_id)) > 0:
            with tempfile.TemporaryDirectory() as dirpath:
                paths = project.assignments_layer.attachments.download(oid=object_id, save_path=dirpath)
                for path in paths:
                    v2_project.assignments_layer.attachments.add(oid=object_id, file_path=path)
    if len(project.assignments_layer.attachments.search("1=1")) == len(
            v2_project.assignments_layer.attachments.search("1=1")):
        logger.info("Attachments successfully migrated")
    else:
        cleanup_project(gis, title)
        raise Exception("Attachments not migrated. Cleaning up new project")

    # Migrate Integrations
    logger.info("Migrating Integrations")
    v2_project.integrations.batch_delete([v2_project.integrations.get("arcgis-navigator")[0]])
    previous_integrations = project.integrations.search()

    # Replacing AT Code with GUID
    for integration in previous_integrations:
        if "assignmentTypes" in integration:
            types = integration["assignmentTypes"]
            key_list = list(sorted(types.keys()))
            for key in key_list:
                at_name = project.assignment_types.get(code=int(key)).name
                guid = get_assignment_type_global_id(new_assignment_types, at_name)
                v2_project.integrations.add(integration_id=integration["id"], prompt=integration["prompt"],
                                            url_template=types[key]["urlTemplate"], assignment_types=guid)
        else:
            v2_project.integrations.add(integration_id=integration["id"], prompt=integration["prompt"],
                                        url_template=integration["urlTemplate"])
    # Get rid of old URL patterns
    integrations = v2_project.integrations.search()
    universal_link_integrations = generate_universal_links(integrations)
    v2_project.integrations.batch_update(universal_link_integrations)
    
    # Migrate Webmaps - Retain non-WF layers
    logger.info("Migrating Webmaps")
    upgrade_webmaps(project.worker_webmap, v2_project.worker_webmap)
    upgrade_webmaps(project.dispatcher_webmap, v2_project.dispatcher_webmap)
    logger.info("Script Completed")


def generate_universal_links(integrations):
    for integration in integrations:
        if integration.url_template:
            if "arcgis-navigator://" in integration.url_template:
                integration.url_template = integration.url_template.replace("arcgis-navigator://", "https://navigator.arcgis.app")
            if "arcgis-collector://" in integration.url_template:
                integration.url_template = integration.url_template.replace("arcgis-collector://", "https://collector.arcgis.app")
            if "arcgis-explorer://" in integration.url_template:
                integration.url_template = integration.url_template.replace("arcgis-explorer://", "https://explorer.arcgis.app")
    return integrations


def upgrade_webmaps(old_webmap, new_webmap):
    new_data = new_webmap.item.get_data()
    old_data = old_webmap.item.get_data()
    expected_layers = len(old_data["operationalLayers"])
    for i, layer in enumerate(old_data["operationalLayers"]):
        if "Workers_0" == layer["id"]:
            old_data["operationalLayers"][i] = get_wf_operational_layer(new_data, "Workers_0")
        elif "Assignments_0" == layer["id"]:
            old_data["operationalLayers"][i] = get_wf_operational_layer(new_data, "Assignments_0")
        else:
            old_data["operationalLayers"][i] = layer
    # retain dispatchers, AT, and integratioons table
    if "tables" in new_data:
        old_data["tables"] = new_data["tables"]
    # remove location tracking layer
    for i, layer in enumerate(old_data["operationalLayers"]):
        if "Location Tracking_0" == layer["id"]:
            old_data["operationalLayers"].pop(i)
            expected_layers = expected_layers - 1
    new_webmap.item.update(item_properties={
        "text": json.dumps(old_data),
        "extent": old_webmap.item.extent
    })
    new_data = new_webmap.item.get_data()
    if not len(new_data["operationalLayers"]) == expected_layers:
        raise Exception("Layers not added successfully")


if __name__ == "__main__":
    # Get all of the commandline arguments
    parser = argparse.ArgumentParser("Migrate Version 1 Project to Version 2")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-org', dest='org_url', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-project-id', dest='project_id', help="The id of the project to migrate", required=True)
    parser.add_argument('-new-title', dest='title', help="The new title of the v2 project to migrate")
    parser.add_argument('-log-file', dest='log_file', help='The log file to use')
    parser.add_argument('--skip-dispatchers', dest='skip_dispatchers', action='store_true',
                        help='Do not migrate dispatchers from v1 project')
    parser.add_argument('--skip-ssl-verification', dest='skip_ssl_verification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
