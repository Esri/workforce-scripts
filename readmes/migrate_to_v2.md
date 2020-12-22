## Migrate Version 1 Workforce Project to V2

NOTE: This script migrates the entire Version 1 Workforce project to a Version 2 project. 
If you've already migrated your project using the Workforce web app and now want to migrate your assignments, please see the script:
[Migrate Assignments](migrate_assignments.md)

This script takes a Version 1 Workforce Project and migrates the entire project to a Version 2 project. It will preserve your assignment, worker, assignment type, webmap, integration and (optionally) dispatcher data in the new project.

**This script requires the logged in user to be an admin or to be the owner of the project and requires a version of the Python API (1.8.3+) which supports Version 2 Projects**

To install the correct version of the Python API, please follow the directions in the README for this repo. Then follow the directions to run the migration script below.

Supports Python 3.5+

----

In addition to the authentication arguments, the script specific arguments are as follows:

- -project-id \<projectId\> - The workforce project ID (from AGOL)
- -new-title \<title\> - (Optional) What you want your new V2 project to be called. If you do not provided a title, by default the name will be "{old title} Upgraded"
- --skip-dispatchers - (Optional) If provided, the dispatcher data will not be migrated (in case you do not want your dispatchers seeing the project yet) 

Example Usage:
```bash
python migrate_to_v2.py -u <username> -p <password> -org https://<org>.maps.arcgis.com -project-id <project-id> -new-title <title>
```

## What it does

 1. First the script creates a new blank version 2 project
 2. Then data is migrated over from your version 1 project to version 2
 
