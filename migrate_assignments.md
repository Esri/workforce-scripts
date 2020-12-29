## Migrate Version 1 Assignments to V2 Project

NOTE: This script migrates just the assignments from your Version 1 Workforce project to a Version 2 project. 
It assumes you have already migrated the project using the "Migrate project" option in the Workforce web app.
If you have not done so and want to migrate the entire project using Python, please see:
[Migrate to V2 Project](readmes/migrate_to_v2.md)

This script takes a Version 1 Workforce Project and migrates the assignments to a Version 2 project. It will preserve your assignment data in the new project. 
It assumes you have used the "Migrate Project" option in the Workforce web app to migrate the project already. 

**This script requires the logged in user to be an admin or to be the owner of the project and requires a version of the Python API (1.8.3+) which supports Version 2 Projects**

To install the correct version of the Python API, please follow the directions in the README for this repo. Then follow the directions to run the migration script below.

Supports Python 3.5+

----

In addition to the authentication arguments, the script specific arguments are as follows:

- -classic-project-id \<projectId\> - The workforce project ID for your classic Workforce Project. This is the item ID of the item with type "Workforce Project"
- -new-project-id \<newProjectId\> - The project ID for your offline-enabled Workforce Project. This is the item ID of the Workforce project's feature service.
- -where - The where clause for the assignments you want to migrate. This is optional - by default, we migrate assignments that are not completed or canceled.

Both project IDs can easily be identified by looking at the URL in the Workforce web app, no matter the project version.
https://workforce.arcgis.com/projects/{project_id}/dispatch

Example Usage 1 - if I only wanted to migrate unassigned assignments:
```bash
python migrate_assignments.py -u <username> -p <password> -org https://<org>.maps.arcgis.com -classic-project-id <project-item-id> -new-project-id <new-project-fs-item-id> -where "status=0"
```

Example Usage 2 - if I wanted to migrate unassigned, assigned, and in progress assignments:
```bash
python migrate_assignments.py -u <username> -p <password> -org https://<org>.maps.arcgis.com -classic-project-id <project-item-id> -new-project-id <new-project-fs-item-id> -where "status IN (0, 1, 2)"
```

## What it does

 1. First the script validates the assignment types and workers have been successfully migrated (using the UI) from your v1 to v2 project.
 2. Then assignments are migrated to the v2 project
 3. Then attachments are migrated to the v2 project
 
 
