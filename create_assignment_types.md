## Create Assignment Types From CSV

This script reads a CSV file containing the assignment types to add to the workforce project.

**This script requires the logged in user to be an admin or to be the owner of the project**

Supports Python 3.5+

----

Consider the following CSV example that is to be imported into Workforce:

`Installation, Removal, Renovation, Demolition`


In addition to the authentication arguments, the script specific arguments are as follows:

- -csv-file \<csvFile\> The csv file to read
- -log-file \<logFile\> The log file to use for logging messages
- -project-id \<projectId\> - The workforce project ID (from AGOL). For a version 1 project, this is the item ID of the Workforce project item. For a version 2 project, this is the item ID of the Workforce feature service (both found in the web app URL "projects/{project_id}/dispatch")

Example Usage:
```bash
python create_assignment_types.py -u <username> -p <password> -org https://<org>.maps.arcgis.com -project-id <project-id> -csv-file ../sample_data/assignment_types.csv -log-file log.txt
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the required token
 2. Then the CSV file is parsed.
 3. The assignment types parsed from the CSV are validated. We don't want any duplicates.
 4. Add the assignment types to the workforce project (assignment feature layer)
