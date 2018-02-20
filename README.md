# Workforce Scripts
A set of python scripts (using multiple libraries) to help administer Workforce projects and services.

Supports Python 3.5+ (required for ArcGIS API for Python)

A set of Python scripts using the [ArcGIS API for Python](https://developers.arcgis.com/python/). These scripts support Workforce in both ArcGIS Online and ArcGIS Enterprise.
Additional, deprecated, scripts using vanilla Python and ArcREST are also available. These deprecated scripts only support Workforce in ArcGIS Online.


## Features

| Functionality                                                        | Script                                                                            
|----------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| [Create Assignments From CSV](create_assignments_from_csv_readme.md) | [create_assignments_from_csv.py](arcgis_api_for_python/create_assignments_from_csv.py)          |
| [Copy Assignments To Feature Service](copy_assignments_fs_readme.md) | [copy_assignments_fs.py](arcgis_api_for_python/copy_assignments_fs.py)                  |
| [Export Assignments to CSV](export_assignments_to_csv_readme.md)     | [export_assignments_from_csv.py](arcgis_api_for_python/export_assignments_from_csv.py)          |
| [Delete Assignments By Query](delete_assignments_by_query_readme.md) | [delete_assignments_by_query.py](arcgis_api_for_python/delete_assignments_by_query.py)          |
| [Check Assignment Completion ](check_completion_location.md)         | [check_completion_location.py](arcgis_api_for_python/check_completion_location.py)            |
| [Import Workers](import_workers.md)                                  | [import_workers.py](arcgis_api_for_python/import_workers.py)                       |
| [Create Assignment Types ](create_assignment_types.md)               | [create_assignment_types.py](arcgis_api_for_python/create_assignment_types.py)              |
| [Delete Assignment Types ](delete_assignment_types.md)               | [create_assignment_types.py](arcgis_api_for_python/create_assignment_types.py)              |
| [Assignment Monitor ](assignment_monitor.md)                         | [assignment_monitor.py](arcgis_api_for_python/assignment_monitor/assignment_monitor.py)|


## Instructions


1. Install ArcGIS API for Python package as described [here](https://developers.arcgis.com/python/guide/install-and-set-up/).
2. Clone or download this repository
3. In terminal/cmd navigate to the `arcgis_api_for_python` folder
4. Install arrow from PyPi using pip and the requirements.txt file (`pip install -r requirements.txt`)
5. You should now be able to run all scripts in the `arcgis_api_for_python` folder (provided you use the correct arguments)


## Resources

 * [ArcGIS API for Python](https://developers.arcgis.com/python)
 * [Workforce for ArcGIS](http://www.esri.com/products/workforce-for-arcgis)
 * [ArcGIS REST API](http://resources.arcgis.com/en/help/arcgis-rest-api)

## Issues

Find a bug or want to request a new feature?  Please let us know by submitting an issue.

## Contributing

Esri welcomes contributions from anyone and everyone.
Please see our [guidelines for contributing](https://github.com/esri/contributing).

## Licensing

Copyright 2016 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

A copy of the license is available in the repository's
[LICENSE](LICENSE) file.
