import argparse
from arcgis.gis import GIS
from arcgis.apps.workforce.project import Project
from arcgis.features import FeatureLayerCollection


def create_joined_view(gis, source_layer, join_layer, primary_key_ield, foreign_key_field, name):
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
    layer_def = generate_layer_definition(source_layer, join_layer, primary_key_ield, foreign_key_field, name)
    fc.manager.add_to_definition(layer_def)
    return new_item


def generate_fields(layer, add_suffix=False):
    fields = []
    suffix = ""
    if add_suffix:
        suffix = f'_{layer.properties["name"].replace(" ", "_")}'
    for f in layer.properties["fields"]:
        if f["name"].lower() == layer.properties["objectIdField"].lower():
            continue
        fields.append({
            "name": f'{f["name"]}{suffix}',
            "alias": f["alias"],
            "source": f["name"]
        })
    return fields


def generate_layer_definition(source_layer, join_layer, primary_key_field, foreign_key_field, name):
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
                            "sourceLayerFields": generate_fields(source_layer),
                            "relatedTables": [
                                {
                                    "name": f"{join_service_name}_join",
                                    "sourceServiceName": f"{join_service_name}",
                                    "sourceLayerId": join_layer.properties["id"],
                                    "sourceLayerFields": generate_fields(join_layer, add_suffix=True),
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
    parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
    parser.add_argument('-org', dest='org', help="The url of the org/portal to use", required=True)
    # Parameters for workforce
    parser.add_argument('-project-id', dest='project_id', help="The id of the project to create the view from", required=True)
    args = parser.parse_args()
    gis = GIS(args.org, args.username, args.password)
    project = Project(gis.content.get(args.project_id))
    assignments_to_types = create_joined_view(gis,
                                              project.assignments_layer,
                                              project.assignment_types_table,
                                              project._assignment_schema.assignment_type,
                                              project._assignment_types.global_id,
                                              "AssignmentsToTypes")
    assignments_to_workers = create_joined_view(gis,
                                              project.assignments_layer,
                                              project.workers_layer,
                                              project._assignment_schema.worker_id,
                                              project._worker_schema.global_id,
                                              "AssignmentsToWorkers")