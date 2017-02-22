## Workforce Scripts (ArcREST)

Workforce scripts that demostrate how to use the [REST API](http://resources.arcgis.com/en/help/arcgis-rest-api/) with python to administer [Workforce](http://workforce.arcgis.com/) projects

Supports Python 2.7+, 3.4+

**Only Supports 'Built-in' Security**

----

Seven example scripts are provided:

 - [Create Assignments From CSV](create_assignments_from_csv.py) ([Documentation](../create_assignments_from_csv_readme.md))
 - [Copy Assignments To Feature Service](copy_assignments_fs.py) ([Documentation](../copy_assignments_fs_readme.md))
 - [Export Assignments To CSV](export_assignments_to_csv.py) ([Documentation](../export_assignments_to_csv_readme.md))
 - [Delete Assignments By Query](delete_assignments_by_query.py) ([Documentation](../delete_assignments_by_query_readme.md))
 - [Check Completion Location/Time](check_completion_location.py) ([Documentation](../check_completion_location.md))
 - [Create Assignment Types](create_assignment_types.py) ([Documentation](../create_assignment_types.md))
 - [Import Workers](import_workers.py) ([Documentation](../import_workers.md))
 
In addition, [workforcehelpers.py](workforcehelpers.py) is supplied to provide common functionality for all of the scripts. This contains:
 - post(url, data) - This submits a simple POST request to the specified url with the specified data
 - get(url, params) - This submits a simple GET request to the specified url with the specified data
 - get_token(org_url, username, password, ...) - This authenticates the username/password with the provided organizational url
 - query_feature_layer(feature_layer_url, token, ...) - This queries a feature layer for features
 - get_feature_layer(feature_layer_url, token) - This gets the feature layer metadata
 - get_assignments_feature_layer_url(org_url, token, projectId) - This gets the assignments feature layer url that is used by the specified project
 - get_workers_feature_layer_url(org_url, token, projectId) - This gets the workers feature layer url that is used by the specified project
 - get_dispatchers_feature_layer_url(org_url, token, projectId) - This gets the dispatchers feature layer url that is used by the specified project
 - get_location_feature_layer_url(org_url, token, projectId) - This gets the location/tracks feature layer url that is used by the specified project
 - get_group_id(org_url, token, projectId) - This gets the group id that the workforce data resides in
----

### Authentication
 
Each script requires certain parameters, however each script also requires authentication parameters. The table below summarizes the authentication parameters that each standalone script expects:

|       Key       |          Description          |
------------------|-------------------------------|
| url             | AGOL or Portal url            |
| username        | username for log in           |
| password        | password for log in           |

----

**Notes:**

These scripts use [Requests](http://docs.python-requests.org/) to easily make GET and POST requests and to support Python 2 and 3.
