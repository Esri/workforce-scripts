import argparse
import logging
import logging.handlers
import sys
from arcgis.gis import GIS
from arcgis.apps.workforce.project import Project
from arcgis.features import FeatureLayerCollection


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
            "currentVersion": 10.2,
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
            "tables": [

            ],
            "name": f"{name}"
        }
    )
    fc = FeatureLayerCollection.fromitem(new_item)
    layer_def = generate_layer_definition(source_layer, join_layer, primary_key_field, foreign_key_field, name,
                                          source_fields, join_fields)
    fc.manager.add_to_definition(layer_def)
    return new_item


def assignment_type_fields(use_joined_name=False):
    """
    Creates the list of field configuration objects to use in the joined layer
    :param use_joined_name: Determines if the source field should be the same as the name (used when creating a view on a view)
    :return: List of field configuration objects
    """
    fields = [
        {
            "name": "assignment_type_description",
            "alias": "Assignment Type",
            "source": "description"
        }
    ]
    if use_joined_name:
        for f in fields:
            f["source"] = f["name"]
    return fields


def worker_fields(use_joined_name=False):
    """
    Creates the list of field configuration objects to use in the joined layer
    :param use_joined_name: Determines if the source field should be the same as the name (used when creating a view on a view)
    :return: List of field configuration objects
    """
    fields = [
        {
            "name": "worker_name",
            "alias": "Worker Name",
            "source": "name"
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
    if use_joined_name:
        for f in fields:
            f["source"] = f["name"]
    return fields


def dispatcher_fields(use_joined_name=False):
    """
    Creates the list of field configuration objects to use in the joined layer
    :param use_joined_name: Determines if the source field should be the same as the name (used when creating a view on a view)
    :return: List of field configuration objects
    """
    fields = [
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
    if use_joined_name:
        for f in fields:
            f["source"] = f["name"]
    return fields


def assignment_fields():
    """
    Creates the list of field configuration objects to use in the joined layer
    :return: List of field configuration objects
    """
    fields = [
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
    return fields


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
    gis = GIS(args.org, args.username, args.password)
    logger.info("Getting Workforce Project...")
    project = Project(gis.content.get(args.project_id))
    logger.info("Phase 1: Joining assignments and assignment types...")
    assignments_to_types = create_joined_view(gis,
                                              project.assignments_layer,
                                              project.assignment_types_table,
                                              project._assignment_schema.assignment_type,
                                              project._assignment_types.global_id,
                                              f"{project.title}_IntermediateView0",
                                              assignment_fields(),
                                              assignment_type_fields())
    logger.info("Phase 2: Joining assignments and workers...")
    assignments_to_workers = create_joined_view(gis,
                                                project.assignments_layer,
                                                project.workers_layer,
                                                project._assignment_schema.worker_id,
                                                project._worker_schema.global_id,
                                                f"{project.title}_IntermediateView1",
                                                assignment_fields(),
                                                worker_fields(),
                                                )
    logger.info("Phase 3: Joining assignments, assignment types, and workers...")
    assignments_types_workers = create_joined_view(gis,
                                                   assignments_to_types.layers[0],
                                                   assignments_to_workers.layers[0],
                                                   project._assignment_schema.global_id,
                                                   project._assignment_schema.global_id,
                                                   f"{project.title}_IntermediateView2",
                                                   assignment_type_fields(True) + assignment_fields(),
                                                   worker_fields(True))
    logger.info("Phase 4: Joining assignments and dispatchers...")
    assignments_to_dispatchers = create_joined_view(gis,
                                                    project.assignments_layer,
                                                    project.dispatchers_layer,
                                                    project._assignment_schema.dispatcher_id,
                                                    project._dispatcher_schema.global_id,
                                                    f"{project.title}_IntermediateView3",
                                                    assignment_fields(),
                                                    dispatcher_fields())
    logger.info("Phase 5: Joining assignments, assignment types, workers, and dispatchers...")
    final_item = create_joined_view(gis,
                                    assignments_types_workers.layers[0],
                                    assignments_to_dispatchers.layers[0],
                                    project._assignment_schema.global_id,
                                    project._assignment_schema.global_id,
                                    f"{project.title}_Joined_View",
                                    assignment_fields() + assignment_type_fields(
                                        True) + worker_fields(True),
                                    dispatcher_fields(True))
    logger.info(f"Final Item: {final_item.title}")
    logger.info("Completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-org', dest='org', help="The url of the org/portal to use", required=True)
    parser.add_argument('-project-id', dest='project_id', help="The id of the project to create the view from",
                        required=True)
    parser.add_argument('-log-file', dest="log_file", help="The file to log to")
    parser.add_argument('--skip-ssl-verification', dest='skip_ssl_verification', action='store_true',
                        help="Verify the SSL Certificate of the server")
    args = parser.parse_args()
    main(args)

