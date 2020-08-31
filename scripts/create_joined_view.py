# -*- coding: UTF-8 -*-
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

   This sample creates a joined view layer combining the 4 Workforce layers and tables
"""

import argparse
import datetime
import logging
import logging.handlers
import sys
import traceback
from arcgis.gis import GIS
from arcgis.apps.workforce.project import Project
from arcgis.features import FeatureLayerCollection
from arcgis.mapping import WebMap


# Define the set of fields to include for each layer in the joined layer

assignment_type_fields = [
    {
        "name": "assignmentType",
        "alias": "Assignment Type",
        "source": "description"
    }
]


assignment_fields = [
    {
        "name": "description",
        "alias": "Description",
        "source": "description"
    },
    {
        "name": "status",
        "alias": "Status",
        "source": "status"
    },
    {
        "name": "notes",
        "alias": "Notes",
        "source": "notes"
    },
    {
        "name": "priority",
        "alias": "Priority",
        "source": "priority"
    },
    {
        "name": "workorderid",
        "alias": "WorkOrder ID",
        "source": "workorderid"
    },
    {
        "name": "duedate",
        "alias": "Due Date",
        "source": "duedate"
    },
    {
        "name": "GlobalID",
        "alias": "GlobalID",
        "source": "GlobalID"
    },
    {
        "name": "location",
        "alias": "Location",
        "source": "location"
    },
    {
        "name": "declinedcomment",
        "alias": "Declined Comment",
        "source": "declinedcomment"
    },
    {
        "name": "assigneddate",
        "alias": "Assigned on Date",
        "source": "assigneddate"
    },
    {
        "name": "inprogressdate",
        "alias": "In Progress Date",
        "source": "inprogressdate"
    },
    {
        "name": "completeddate",
        "alias": "Completed on Date",
        "source": "completeddate"
    },
    {
        "name": "declineddate",
        "alias": "Declined on Date",
        "source": "declineddate"
    },
    {
        "name": "pauseddate",
        "alias": "Paused on Date",
        "source": "pauseddate"
    },
    {
        "name": "CreationDate",
        "alias": "Creation Date",
        "source": "CreationDate"
    },
    {
        "name": "Creator",
        "alias": "Creator",
        "source": "Creator"
    },
    {
        "name": "EditDate",
        "alias": "Edit Date",
        "source": "EditDate"
    },
    {
        "name": "Editor",
        "alias": "Editor",
        "source": "Editor"
    }
]


worker_fields = [
    {
        "name": "worker_name",
        "alias": "Worker Name",
        "source": "name"
    },
    {
        "name": "worker_title",
        "alias": "Worker Title",
        "source": "title"
    },
    {
        "name": "worker_status",
        "alias": "Worker Status",
        "source": "status"
    },
    {
        "name": "worker_contactnumber",
        "alias": "Worker Contact Number",
        "source": "contactnumber"
    },
    {
        "name": "worker_notes",
        "alias": "Worker Notes",
        "source": "notes"
    }
]

dispatcher_fields = [
    {
        "name": "dispatcher_name",
        "alias": "Dispatcher Name",
        "source": "name"
    },
    {
        "name": "dispatcher_contactnumber",
        "alias": "Dispatcher Contact Number",
        "source": "contactnumber"
    }
]


def create_joined_view(gis, source_layer, join_layer, primary_key_field, foreign_key_field, name, source_fields,
                       join_fields):
    """
    Create a joined layer view between 2 layers
    :param gis: The gis to create the layer with
    :param source_layer: The source layer to join
    :param join_layer: The layer to join with the source layer
    :param primary_key_field: The primary key field in the source layer
    :param foreign_key_field: The foreign key field in the join layer
    :param name: The name of the new layer that will be created
    :param source_fields: The list of field configuration objects in the source layer to keep in the resulting joined layer
    :param join_fields: The list of field configuration objects in the join layer to keep in the resulting joined layer
    :return: The new item
    """
    new_item = gis.content.create_service(
        name=name,
        is_view=True,
        create_params={
            "currentVersion": 10.7,
            "serviceDescription": "",
            "hasVersionedData": False,
            "supportsDisconnectedEditing": False,
            "hasStaticData": True,
            "maxRecordCount": 2000,
            "supportedQueryFormats": "JSON",
            "capabilities": "Query",
            "description": "",
            "copyrightText": "",
            "allowGeometryUpdates": False,
            "syncEnabled": False,
            "editorTrackingInfo": {
                "enableEditorTracking": False,
                "enableOwnershipAccessControl": False,
                "allowOthersToUpdate": True,
                "allowOthersToDelete": True
            },
            "xssPreventionInfo": {
                "xssPreventionEnabled": True,
                "xssPreventionRule": "InputOnly",
                "xssInputRule": "rejectInvalid"
            },
            "tables": [],
            "name": f"{name}"
        }
    )
    fc = FeatureLayerCollection.fromitem(new_item)
    layer_def = generate_layer_definition(source_layer, join_layer, primary_key_field, foreign_key_field, name,
                                          source_fields, join_fields)
    fc.manager.add_to_definition(layer_def)
    return new_item


def change_source_field_name_to_joined_field_name(fields):
    """
    Switches the source of the field name to be the name of the field after it was added to a joined layer
    :param fields: The list of field objects
    """
    for f in fields:
        f["source"] = f["name"]


def generate_layer_definition(source_layer, join_layer, primary_key_field, foreign_key_field, name, source_fields,
                              join_fields):
    """
    Create layer definition for a joined layer view between 2 layers
    :param source_layer: The source layer to join
    :param join_layer: The layer to join with the source layer
    :param primary_key_field: The primary key field in the source layer
    :param foreign_key_field: The foreign key field in the join layer
    :param name: The name of the new layer that will be created
    :param source_fields: The list of field configuration objects in the source layer to keep in the resulting joined layer
    :param join_fields: The list of field configuration objects in the join layer to keep in the resulting joined layer
    :return: The layer definition
    """
    join_service_name = join_layer.url.split("/")[-3]
    source_service_name = source_layer.url.split("/")[-3]
    layer_def = {
        "layers": [
            {
                "name": f"{name}",
                "displayField": "",
                "description": "AttributeJoin",
                "adminLayerInfo": {
                    "viewLayerDefinition": {
                        "table": {
                            "name": f"{source_service_name}_target",
                            "sourceServiceName": f"{source_service_name}",
                            "sourceLayerId": source_layer.properties["id"],
                            "sourceLayerFields": source_fields,
                            "relatedTables": [
                                {
                                    "name": f"{join_service_name}_join",
                                    "sourceServiceName": f"{join_service_name}",
                                    "sourceLayerId": join_layer.properties["id"],
                                    "sourceLayerFields": join_fields,
                                    "type": "LEFT",
                                    "parentKeyFields": [
                                        f"{primary_key_field}"
                                    ],
                                    "keyFields": [
                                        f"{foreign_key_field}"
                                    ],
                                    "topFilter": {
                                        "groupByFields": "GlobalID",
                                        "orderByFields": "OBJECTID ASC",
                                        "topCount": 1
                                    }
                                }
                            ],
                            "materialized": False
                        }
                    },
                    "geometryField": {
                        "name": f"{source_service_name}_target.Shape"
                    }
                }
            }
        ]
    }
    return layer_def


def main(args):
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
    if args.log_file:
        rh = logging.handlers.RotatingFileHandler(args.log_file, mode='a', maxBytes=10485760)
        rh.setFormatter(formatter)
        rh.setLevel(logging.DEBUG)
        logger.addHandler(rh)
    # Add the handlers to the root logger
    logger.addHandler(sh)

    # Create the GIS
    logger.info("Authenticating...")
    gis = GIS(args.org, args.username, args.password, verify_cert=not args.skip_ssl_verification)
    if gis.properties["isPortal"]:
        raise RuntimeError("This script only works with ArcGIS Online")
    logger.info("Getting Workforce Project...")
    item = gis.content.get(args.project_id)
    if item is None:
        raise RuntimeError("Invalid Project Id")
    project = Project(gis.content.get(args.project_id))
    try:
        if not project._is_v2_project:
            raise Exception(
                "The project provided is not a v2 project. You can only use v2 (offline-enabled) projects with this script")
    except AttributeError:
        raise Exception(
            "Cannot find the attribute is v2 project. Are you sure you have the API version 1.8.3 or greater installed? Check with `arcgis.__version__` in your Python console")
    logger.info("Phase 1: Joining assignments to assignment types...")
    d = int(datetime.datetime.now().timestamp())
    assignments_to_types = create_joined_view(gis,
                                              project.assignments_layer,
                                              project.assignment_types_table,
                                              project._assignment_schema.assignment_type,
                                              project._assignment_types.global_id,
                                              f"{project.title} Intermediate View 0 {d}",
                                              assignment_fields,
                                              assignment_type_fields)
    logger.info("Phase 2: Joining assignments to workers...")
    assignments_to_workers = create_joined_view(gis,
                                                project.assignments_layer,
                                                project.workers_layer,
                                                project._assignment_schema.worker_id,
                                                project._worker_schema.global_id,
                                                f"{project.title} Intermediate View 1 {d}",
                                                assignment_fields,
                                                worker_fields,
                                                )
    logger.info("Phase 3: Joining assignments to dispatchers...")
    assignments_to_dispatchers = create_joined_view(gis,
                                                    project.assignments_layer,
                                                    project.dispatchers_layer,
                                                    project._assignment_schema.dispatcher_id,
                                                    project._dispatcher_schema.global_id,
                                                    f"{project.title} Intermediate View 2 {d}",
                                                    assignment_fields,
                                                    dispatcher_fields)
    change_source_field_name_to_joined_field_name(assignment_type_fields)
    change_source_field_name_to_joined_field_name(worker_fields)
    change_source_field_name_to_joined_field_name(dispatcher_fields)
    logger.info("Phase 4: Joining assignments and assignment types to assignments and workers...")
    assignments_types_workers = create_joined_view(gis,
                                                   assignments_to_types.layers[0],
                                                   assignments_to_workers.layers[0],
                                                   project._assignment_schema.global_id,
                                                   project._assignment_schema.global_id,
                                                   f"{project.title} Intermediate View 3 {d}",
                                                   assignment_type_fields + assignment_fields,
                                                   worker_fields)
    logger.info("Phase 5: Joining assignments and types and workers to  assignments and workers...")
    if args.name:
        name = args.name
    else:
        name = f"{project.title} Joined View {d}"
    final_item = create_joined_view(gis,
                                    assignments_types_workers.layers[0],
                                    assignments_to_dispatchers.layers[0],
                                    project._assignment_schema.global_id,
                                    project._assignment_schema.global_id,
                                    name,
                                    assignment_fields + assignment_type_fields+ worker_fields,
                                    dispatcher_fields)
    logger.info(f"Final Item: {final_item.title}")
    if args.create_dashboard:
        logger.info("Creating dashboard")
        
        # create new webmap
        map_item = project.dispatcher_webmap.save(
            item_properties={"title": project.title + " Dashboard Map", "tags": [], "snippet": "Dashboard Map"})
        new_webmap = WebMap(map_item)
        
        # swizzle in joined layer instead of assignments layer
        for i, layer in enumerate(new_webmap.layers):
            if layer["id"] == "Assignments_0":
                new_webmap.remove_layer(layer)
                new_webmap.add_layer(final_item)
                new_webmap.layers[i]["id"] = "Assignments_0"
                break
        new_webmap.update()
        
        # clone dashboard with your data instead of our data
        item = gis.content.get("af7cd356c21a4ded87d8cdd452fd8be3")
        item_mapping = {'377b2b2014f24b0ab9b053d9b2fed113': final_item.id,
                        'e1904f5c56484163a021155f447adf34': project.workers_item.id,
                        'bb7d2b495ecc4ea7810b28f16ef71cba': new_webmap.item.id}
        cloned_items = gis.content.clone_items([item], item_mapping=item_mapping, search_existing_items=False)
        if len(cloned_items) == 0:
            raise ValueError("Creating dashboard failed")
            
        # Save new name and share to group
        logger.info("Updating title and sharing to project group")
        new_title = project.title + " Dashboard"
        cloned_items[0].update(item_properties={"title": new_title},
                               thumbnail="https://www.arcgis.com/apps/opsdashboard/assets/images/no-dashboard-thumb-84c2afc9d73774823c7865b4cc776b9b.png")
        cloned_items[0].share(groups=[project.group])
        logger.info("Dashboard creation completed")
    logger.info("Script completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Creates a hosted view layer that joins the 4 offline-enabled Workforce layers/tables together")
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-org', dest='org', help="The url of the org/portal to use", required=True)
    parser.add_argument('-project-id', dest='project_id', help="The id of the project to create the view from",
                        required=True)
    parser.add_argument('--create-dashboard', dest='create_dashboard', action='store_true', help="Create a dashboard using the joined view in AGOL")
    parser.add_argument('-log-file', dest="log_file", help="The file to log to")
    parser.add_argument('--skip-ssl-verification', dest='skip_ssl_verification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    parser.add_argument('-name', dest='name', help="The name of the resulting joined view")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        logging.getLogger().critical("Exception detected, script exiting")
        logging.getLogger().critical(e)
        logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))

