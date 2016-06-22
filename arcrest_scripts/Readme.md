## Workforce Scripts (ArcREST)

Workforce scripts that demonstrate how to use the [ArcREST](https://github.com/Esri/ArcREST) python library to administer [Workforce](http://workforce.arcgis.com/) projects

It is recommend to install ArcREST from source by cloning the repo (or downloading as zip) and running python setup.py install.

Supports Python 2.7+, 3.4+

----
 - [Create Assignments From CSV](create_assignments_from_csv.py) ([Documentation](../create_assignments_from_csv_readme.md))
 - [Copy Assignments To Feature Service](copy_assignments_fs.py) ([Documentation](../copy_assignments_fs_readme.md))
 - [Export Assignments To CSV](export_assignments_to_csv.py) ([Documentation](../export_assignments_to_csv_readme.md))
 - [Delete Assignments By Query](delete_assignments_by_query.py) ([Documentation](../delete_assignments_by_query_readme.md))
 - [Check Completion Location/Time](check_completion_location.py) ([Documentation](../check_completion_location.md))

In addition, [workforcehelpers.py](workforcehelpers.py) is supplied to provide common functionality for all of the scripts. This contains:
 - get_security_hander(args) - This uses the provided arguments to create a [securityhandlerhelper](https://github.com/Esri/ArcREST/blob/master/src/arcresthelper/securityhandlerhelper.py) which is used to authenticate with ArcGIS Online
 - get_assignments_feature_layer(shh, projectId) - This gets the assignments feature layer based on the workforce projectId
 - get_dispatchers_feature_layer(shh, projectId) - This gets the dispatcher feature layer based on the workforce projectId
 - get_location_feature_layer(shh, projectId) - This gets the location feature layer based on the workforce projectId
 - get_workers_feature_layer(shh, projectId) - This gets the workers feature layer based on the workforce projectId
 - initialize_logging(logFile) - This sets the root level python logger to output to the console as well as to the log file

----

### Authentication
 
Each script requires certain parameters, however each script also requires some sort of authentication parameters. The table below summarizes the authentication parameters that ArcREST expects for different security types:

|       Key       |          Description          |       Required?         |
------------------|-------------------------------|--------------------------
| url             | AGOL or Portal url            | YES                     |
| security_type   | security type used to connect | See Values *            |
| username        | username for log in           | ``LDAP|NTLM`` **        |
| password        | password for log in           | ``LDAP|NTLM`` **        |
| proxy_url       | url for proxy server          | Optional                |
| proxy_port      | port for proxy server         | Optional                |
| token_url       | url for token server          | Optional                |
| referer_url     | url for referer               | Optional                |
| certificatefile |                               | ``PKI``                 |
| keyfile         |                               | ``PKI``                 |
| client_id       |                               | ``OAuth``               |
| secret_id       |                               | ``OAuth``               |
| \* Values: ``ArcGIS|Portal|LDAP|NTLM|PKI|OAuth`` (defaults to ``Portal``) |
| \*\* Also required for ``ArcGIS|Portal`` unless using anonymous logins    |

Example ('Portal'/'Built-in'):
```
python delete_assignments.py -u username -p password -url "https://nitro.maps.arcgis.com" ...
```
