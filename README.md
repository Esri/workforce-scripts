# Workforce Scripts
A set of Python scripts and notebooks to help administer and configure Workforce projects.

## Notebooks

Several example Jupyter notebooks are provided to demonstrate some more advanced workflows that are possible via the ArcGIS API for Python and Workforce:
- [1 - Configuring a Project](notebooks/examples/1%20-%20Configuring%20a%20Project.ipynb)
- [2 - Importing Assignments](notebooks/examples/2%20-%20Importing%20Assignments.ipynb)
- [3 - Assigning Work](notebooks/examples/3%20-%20Assigning%20Work.ipynb)
- [4 - Optimally Creating and Assigning Work Orders Based on Routes](notebooks/examples/4%20-%20Optimally%20Creating%20and%20Assigning%20Work%20Orders%20Based%20on%20Routes.ipynb)

Notebooks used for previous demos are also available:
- [UC 2018](notebooks/UC_2018)

## Scripts

Supports:
- Python 3.5+
- Python API for ArcGIS 1.4.1+

A set of Python scripts using the [ArcGIS API for Python v1.4.1+](https://developers.arcgis.com/python/).
These scripts support Workforce in both ArcGIS Online and ArcGIS Enterprise.



### Features

| Functionality                                                        | Script                                                                            
|----------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| [Create Assignment Types ](create_assignment_types.md)               | [create_assignment_types.py](scripts/create_assignment_types.py)              |
| [Import Workers](import_workers.md)                                  | [import_workers.py](scripts/import_workers.py)                       |
| [Import Dispatchers](import_dispatchers.md)                          | [import_dispatchers.py](scripts/import_dispatchers.py)
| [Create Assignments From CSV](create_assignments_from_csv_readme.md) | [create_assignments_from_csv.py](scripts/create_assignments_from_csv.py)          |
| [Copy Assignments To Feature Service](copy_assignments_to_fs_readme.md) | [copy_assignments_to_fs.py](scripts/copy_assignments_to_fs.py)                  |
| [Export Assignments to CSV](export_assignments_to_csv_readme.md)     | [export_assignments_from_csv.py](scripts/export_assignments_from_csv.py)          |
| [Check Assignment Completion Location](check_completion_location.md)         | [check_completion_location.py](scripts/check_completion_location.py)            |
| [Delete Assignments](delete_assignments_readme.md)                   | [delete_assignments.py](scripts/delete_assignments.py)          |                   |
| [Delete Assignment Types ](delete_assignment_types.md)               | [create_assignment_types.py](scripts/create_assignment_types.py)              |
| [Assignment Monitor (Slack Integration)](assignment_monitor.md)                           | [assignment_monitor.py](scripts/assignment_monitor.py) |



### Instructions


1. Install ArcGIS API for Python package as described [here](https://developers.arcgis.com/python/guide/install-and-set-up/).
2. Clone or download this repository
3. In terminal/cmd navigate to the `scripts` folder
4. Install arrow from PyPi using pip and the requirements.txt file (`pip install -r requirements.txt`)
5. You should now be able to run all scripts in the `scripts` folder (provided you use the correct arguments)


## Resources

 * [ArcGIS API for Python](https://developers.arcgis.com/python)
 * [Workforce for ArcGIS](http://www.esri.com/products/workforce-for-arcgis)

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
