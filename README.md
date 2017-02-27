# Workforce Scripts
A set of python scripts (using multiple libraries) to help administer Workforce projects and services

Supports Python 2.7+ and Python 3.4+ (required for ArcGIS API for Python)

Three sets of scripts that do the same things are provided. [One](arcrest_scripts) relies on the [ArcREST](https://github.com/Esri/ArcREST) library. A [second](arcgis_api_for_python_scripts) set relies on [ArcGIS API for Python](https://developers.arcgis.com/python/). The [stand-a-lone](standalone_scripts) set of scripts are standalone and uses [Requests](http://docs.python-requests.org/) to make GET and POST requests easily and to support Python 2 and 3.

## Features

| Functionality                                                        | Link                                                                                                                       | Script Name                    |
|----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| [Create Assignments From CSV](create_assignments_from_csv_readme.md) | [ArcGIS API For Python](arcgis_api_for_python/create_assignments_from_csv.py) [ArcREST](arcrest_scripts/create_assignments_from_csv.py)  [Standalone](standalone_scripts/create_assignments_from_csv.py) | create_assignments_from_csv.py |
| [Copy Assignments To Feature Service](copy_assignments_fs_readme.md) | [ArcGIS API For Python](arcgis_api_for_python/copy_assignments_fs.py)[ArcREST](arcrest_scripts/copy_assignments_fs.py)  [Standalone](standalone_scripts/copy_assignments_fs.py)                 | copy_assignments_fs.py         |
| [Export Assignments to CSV](export_assignments_to_csv_readme.md)     | [ArcGIS API For Python](arcgis_api_for_python/export_assignments_from_csv.py)[ArcREST](arcrest_scripts/export_assignments_to_csv.py)  [Standalone](standalone_scripts/export_assignments_to_csv.py)     | export_assignments_to_csv.py   |
| [Delete Assignments By Query](delete_assignments_by_query_readme.md) | [ArcGIS API For Python](arcgis_api_for_python/delete_assignments_by_query.py)[ArcREST](arcrest_scripts/delete_assignments_by_query.py)  [Standalone](standalone_scripts/delete_assignments_by_query.py) | delete_assignments_by_query.py |
| [Check Assignment Completion ](check_completion_location.md)         | [ArcGIS API For Python](arcgis_api_for_python/check_completion_location.py)[ArcREST](arcrest_scripts/check_completion_location.py) [Standalone](standalone_scripts/check_completion_location.py)      | check_completion_location.py   |
| [Import Workers](import_workers.md)                                  | [ArcGIS API For Python](arcgis_api_for_python/import_workers.py)[Standalone](standalone_scripts/import_workers.py)                                                                         | import_workers.py              |
| [Create Assignment Types ](create_assignment_types.md)               | [Standalone](standalone_scripts/create_assignment_types.py)                                                                | create_assignment_types.py     |


## Why are there so many choices?

We provided three different options to use Python to help automate common workflows within Workforce For ArcGIS. 

- If you plan to integrate Workforce with many other systems, it's probably best if you use the stand-a-lone scripts.
- If you have existing workflows that use ArcREST for other ArcGIS related scripts, it's probably best if you use the ArcREST scripts.
- If you are relatively new to Python, have interest in using other geoprocessing analytics, or would like to use [Jupyter](https://jupyter.org/) notebooks, it's probably best if you use the ArcGIS API for Python scripts.

## Instructions

#### ArcGIS API for Python

1. Install Conda and the ArcGIS API for Python package as described [here](https://developers.arcgis.com/python/guide/install-and-set-up/).
2. Clone or download this repository
3. You should now be able to run all scripts in the `arcgis_api_for_python` folder (provided you use the correct arguments)

#### ArcREST

1. Install Python 2.7.x or 3.4+ if not already installed
2. Clone or download this repository
3. In terminal/cmd navigate to the `arcrest_scripts` folder
4. Install ArcREST form PyPi using pip and the requirements.txt file (`pip install -r requirements.txt`)
5. You should now be able to run all script in the `arcrest_scripts` folder (provided you use the correct arguments)

#### Standalone

1. Install Python 2.7.x or 3.4+ if not already installed
2. Clone or download this repository
3. In terminal/cmd navigate to the `standalone_scripts` folder
4. Install requests form PyPi using pip and the requirements.txt file (`pip install -r requirements.txt`)
5. You should now be able to run all script in the `standalone_scripts` folder (provided you use the correct arguments)

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
