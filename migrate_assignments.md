## Migrate Version 1 Assignments to V2 Project

NOTE: This script migrates just the assignments from your Version 1 Workforce project to a Version 2 project. 
It assumes you have already migrated the project using the "Migrate project" option in the Workforce web app.
If you have not done so and want to migrate the entire project using Python, please see:
[Migrate to V2 Project](migrate_to_v2.md)

This script takes a Version 1 Workforce Project and migrates the assignments to a Version 2 project. It will preserve your assignment data in the new project. 
It assumes you have used the "Migrate Project" option in the Workforce web app to migrate the project already. 

**This script requires the logged in user to be an admin or to be the owner of the project and requires a version of the Python API (1.8.3+) which supports Version 2 Projects**

To install the correct version of the Python API, please follow the directions in the README for this repo. Then follow the directions to run the migration script below.

Supports Python 3.5+

----

In addition to the authentication arguments, the script specific arguments are as follows:

- -classic-project-id \<projectId\> - The workforce project ID for your classic Workforce Project. This is the item ID of the item with type "Workforce Project"
- -new-project-id \<newProjectId\> - The project ID for your offline-enabled Workforce Project. This is the item ID of the Workforce project's feature service.
- --skip-dispatchers - (Optional) If provided, the dispatcher data will not be migrated (in case you do not want your dispatchers seeing the project yet) 

Example Usage:
```bash
python migrate_to_v2.py -u <username> -p <password> -org https://<org>.maps.arcgis.com -project-id <project-id> -new-title <title>
```

## What it does

 1. First the script validates the assignment types and workers have been successfully migrated (using the UI) from your v1 to v2 project.
 2. Then assignments are migrated to the v2 project
 3. Then attachments are migrated to the v2 project
 
