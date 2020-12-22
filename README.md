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
- [Dev Summit 2019](notebooks/dev_summit_2019)
- [UC 2019](notebooks/UC_2019)
- [Dev Summit 2020](notebooks/dev_summit_2020)

In addition, we have uploaded our AGOL-compatible notebooks into a publicly accessible [group of Hosted Notebooks in ArcGIS Online](https://arcgis.com/home/group.html?id=c1695c0c2f9945a8a7fee7dd106c74ae)

## Scripts

Supports:
- Python 3.6+
- Python API for ArcGIS 1.8.3+

The Workforce team released a new version of the app supporting offline-enabled Projects in July 2020. To work with
those projects in Python and deploy the corresponding scripts in this repo, users will need to update their version
of the Python API to 1.8.3. This can be downloaded in Conda prior to 1.8.3's official release via:

`conda install -c esri/label/prerelease -c esri arcgis`

A set of Python scripts using the [ArcGIS API for Python v1.8.3+](https://developers.arcgis.com/python/).
These scripts support Workforce in both ArcGIS Online and ArcGIS Enterprise.

Note that some may scripts may work with a Python API for ArcGIS version that is less than 1.8.3 but this cannot 
be guaranteed.

### Features

| Functionality                                                        | Script                                                                            
|----------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| [Create Assignment Types ](markdown/create_assignment_types.md)               | [create_assignment_types.py](scripts/create_assignment_types.py)              |
| [Import Workers](markdown/import_workers.md)                                  | [import_workers.py](scripts/import_workers.py)                       |
| [Import Dispatchers](markdown/import_dispatchers.md)                          | [import_dispatchers.py](scripts/import_dispatchers.py)
| [Create Assignments From CSV](markdown/create_assignments_from_csv_readme.md) | [create_assignments_from_csv.py](scripts/create_assignments_from_csv.py)          |
| [Copy Assignments To Feature Service](markdown/copy_assignments_to_fs_readme.md) | [copy_assignments_to_fs.py](scripts/copy_assignments_to_fs.py)                  |
| [Export Assignments to CSV](markdown/export_assignments_to_csv_readme.md)     | [export_assignments_from_csv.py](scripts/export_assignments_from_csv.py)          |
| [Check Assignment Completion Location](markdown/check_completion_location.md)         | [check_completion_location.py](scripts/check_completion_location.py)            |
| [Delete Assignments](markdown/delete_assignments_readme.md)                   | [delete_assignments.py](scripts/delete_assignments.py)          |                   |
| [Delete Assignment Types ](markdown/delete_assignment_types.md)               | [create_assignment_types.py](scripts/create_assignment_types.py)              |
| [Assignment Monitor (Slack Integration)](markdown/assignment_monitor.md)                           | [assignment_monitor.py](scripts/assignment_monitor.py) |
| [Migrate to Version 2 Project](markdown/migrate_to_v2.md) | [migrate_to_v2.py](scripts/migrate_to_v2.py) |
| [Reset Stale Workers ](markdown/reset_stale_workers.md)               | [reset_stale_workers.py](scripts/reset_stale_workers.py)              |
| [Report Incomplete Assignments with Work Orders ](markdown/report_incomplete_assignments_with_work_orders.md)               | [report_incomplete_assignments_with_work_orders.py](scripts/report_incomplete_assignments_with_work_orders.py)    
| [Report Complete Assignments without Work Orders](markdown/report_complete_assignments_without_work_orders.md)               | [report_complete_assignments_without_work_orders.py](scripts/report_complete_assignments_without_work_orders.py)    
| [Create Default Ops Dashboard](markdown/create_ops_dashboard.md)              | [create_ops_dashboard.py](scripts/create_ops_dashboard.py)|
| [Create Joined View](markdown/create_joined_view.md) | [create_joined_view](scripts/created_joined_view.py) |

### Instructions


1. Install ArcGIS API for Python package via Conda as described [here](https://developers.arcgis.com/python/guide/install-and-set-up/).
2. Clone or download this repository
3. In terminal/cmd navigate to the `scripts` folder
4. Create Conda environment (which automatically comes with 1.8.3 prerelease of the Python API)
   1. Install Anaconda
   2. Run `conda env create --file environment.yml` to create the virtual environment with the correct dependencies
   3. Run `conda activate workforce-scripts` to activate the environment
5. (Optional - dev only) Configure pre-commit to run flake8 linting on pushes
   * `pre-commit install --hook-type pre-push`

To run in ArcGIS Notebooks:
1. Visit our [AGOL Hosted Notebooks group](https://arcgis.com/home/group.html?id=c1695c0c2f9945a8a7fee7dd106c74ae#overview)
2. Click on "Content"
3. Choose a notebook you'd like
4. Click on the thumbnail for "Open Notebook" to open in ArcGIS Notebooks

## Resources

 * [ArcGIS API for Python](https://developers.arcgis.com/python)
 * [Workforce for ArcGIS](http://www.esri.com/products/workforce-for-arcgis)
 * [Usecases for the Workforce Python module](https://www.esri.com/arcgis-blog/products/workforce/field-mobility/automate-workforce-with-arcgis-api-for-python/)
 * [Scheduling Workforce Python scripts with Windows Task Scheduler](https://community.esri.com/groups/workforce-for-arcgis/blog/2020/05/14/schedule-tasks-for-workforce)
 * [Scheduling Workforce Python scripts in Linux / MacOS](markdown/scheduling_with_python.md)

## Issues

Find a bug or want to request a new feature?  Please let us know by submitting an issue.

## Contributing

Esri welcomes contributions from anyone and everyone.
Please see our [guidelines for contributing](https://github.com/esri/contributing).

## Licensing

Copyright 2020 Esri

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
