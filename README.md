# Workforce Scripts
A set of python scripts to help administer Workforce

Supports Python 2.7+ and Python 3.4+

Two sets of scripts that do the same things are provided. [One](arcrest_scripts) relies on the [ArcREST](https://github.com/Esri/ArcREST) library (highly recommend to install latest master branch as recent changes have been made to fix bugs). The [other](standalone_scripts) set of scripts are standalone and uses [Requests](http://docs.python-requests.org/) to make GET and POST requests easily and to support Python 2 and 3. This 3rd party library has been bundled with the scripts.

If you plan to use ArcREST, it is recommend to install it from source by cloning the repo (or downloading as zip) and running python setup.py install.

| Functionality                                                        | Link                                                                                                                       | Script Name                    |
|----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| [Create Assignments From CSV](create_assignments_from_csv_readme.md) | [ArcREST](arcrest_scripts/create_assignments_from_csv.py)  [Standalone](standalone_scripts/create_assignments_from_csv.py) | create_assignments_from_csv.py |
| [Copy Assignments To Feature Service](copy_assignments_fs_readme.md) | [ArcREST](arcrest_scripts/copy_assignments_fs.py)  [Standalone](standalone_scripts/copy_assignments_fs.py)                 | copy_assignments_fs.py         |
| [Export Assignments to CSV](export_assignments_to_csv_readme.md)     | [ArcREST](arcrest_scripts/export_assignments_to_csv.py)  [Standalone](standalone_scripts/export_assignments_to_csv.py)     | export_assignments_to_csv.py   |
| [Delete Assignments By Query](delete_assignments_by_query_readme.md) | [ArcREST](arcrest_scripts/delete_assignments_by_query.py)  [Standalone](standalone_scripts/delete_assignments_by_query.py) | delete_assignments_by_query.py |
| [Check Assignment Completion ](check_completion_location.md)         | [ArcREST](arcrest_scripts/check_completion_location.py) [Standalone](standalone_scripts/check_completion_location.py)      | check_completion_location.py   |