## Delete Assignment Types

This script deletes the assignment types in a specified workforce project.

**This script requires the logged in user to be an admin or to be the owner of the project**


Supports Python 3.5+

----

In addition to the authentication arguments, the script specific arguments are as follows:

- -log-file \<log-file\> The log file to use for logging messages
- -project-id \<project-id\> - The workforce project ID (from AGOL). For a version 1 project, this is the item ID of the Workforce project item. For a version 2 project, this is the item ID of the Workforce feature service (both found in the web app URL "projects/{project_id}/dispatch")

Example Usage:
```bash
python delete_assignment_types.py -u <username> -p <password> -org https://<org>.maps.arcgis.com -project-id <project-id> -log-file log.txt
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL or Portal
 2. Deletes the assignment types in the workforce project
