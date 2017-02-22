# Workforce Scripts
A set of python scripts to help administer Workforce projects and services

Supports Python 2.7+ and Python 3.4+

Two sets of scripts that do the same things are provided. [One](arcrest_scripts) relies on the [ArcREST](https://github.com/Esri/ArcREST) library. The [other](standalone_scripts) set of scripts are standalone and uses [Requests](http://docs.python-requests.org/) to make GET and POST requests easily and to support Python 2 and 3.

## Features

| Functionality                                                        | Link                                                                                                                       | Script Name                    |
|----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| [Create Assignments From CSV](create_assignments_from_csv_readme.md) | [ArcREST](arcrest_scripts/create_assignments_from_csv.py)  [Standalone](standalone_scripts/create_assignments_from_csv.py) | create_assignments_from_csv.py |
| [Copy Assignments To Feature Service](copy_assignments_fs_readme.md) | [ArcREST](arcrest_scripts/copy_assignments_fs.py)  [Standalone](standalone_scripts/copy_assignments_fs.py)                 | copy_assignments_fs.py         |
| [Export Assignments to CSV](export_assignments_to_csv_readme.md)     | [ArcREST](arcrest_scripts/export_assignments_to_csv.py)  [Standalone](standalone_scripts/export_assignments_to_csv.py)     | export_assignments_to_csv.py   |
| [Delete Assignments By Query](delete_assignments_by_query_readme.md) | [ArcREST](arcrest_scripts/delete_assignments_by_query.py)  [Standalone](standalone_scripts/delete_assignments_by_query.py) | delete_assignments_by_query.py |
| [Check Assignment Completion ](check_completion_location.md)         | [ArcREST](arcrest_scripts/check_completion_location.py) [Standalone](standalone_scripts/check_completion_location.py)      | check_completion_location.py   |
| [Create Assignment Types ](create_assignment_types.md)               | [Standalone](standalone_scripts/create_assignment_types.py)                                                                | create_assignment_types.py     |
| [Import Workers](import_workers.md)                                  | [Standalone](standalone_scripts/import_workers.py)                                                                         | import_workers.py              |

## Instructions

1. Install Python 2.7.x or Python 3.4.x+ if not already installed
2. Install dependencies `pip install -r requirements.txt`
  1. Installs [ArcREST](https://github.com/Esri/ArcREST)
  2. Installs [Requests](http://docs.python-requests.org/en/master/user/install/#install)
4. Clone this repo or download as zip and extract
5. Run the sample scripts with the sample data against your feature services and projects

## Resources

 * [Workforce for ArcGIS](http://www.esri.com/products/workforce-for-arcgis)
 * [ArcGIS REST API](http://resources.arcgis.com/en/help/arcgis-rest-api/)

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
