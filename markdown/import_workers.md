## Import Workers from CSV

This script reads a CSV file containing the required fields to add workers (named users) to the workforce project.

**This script requires the logged in user to be an admin or to be the owner of the project**

Supports Python 3.5+

----

Consider the following CSV example table that is to be imported into Workforce:

| name     | status | title      | contactNumber | userId       | 
|----------|--------|------------|---------------|------------|
| Jane Doe | 0      | Inspector  | 123-456-7890  | jane_doe   |



Due to the various naming conventions organizations may have, this script has many options allowing the user to specify the names of each column. In addition to the authentication arguments, the script specific arguments are as follows:

- -csv-file \<csvFile\> The csv file to read
- -log-file \<logFile\> The log file to use for logging messages
- -project-id \<projectId\> The workforce project ID (from AGOL). For a version 1 project, this is the item ID of the Workforce project item. For a version 2 project, this is the item ID of the Workforce feature service (both found in the web app URL "projects/{project_id}/dispatch")
- -name-field \<nameField\> The name of the column that stores the workers name
- -status-field \<statusField\> The name of the column that stores the workers status. Statuses should be "not_working", "working", or "on_break".
- -user-id-field \<userIdField\> The name of the column that stores the workers named user username
- -title-field \<titleField\> (optional) The name of the column that stores the workers title
- -contact-number-field \<contactNumberField\> (optional) The name of the column that stores the workers contact number

Example Usage:
```bash
python import_workers.py -u <username> -p <password> -org https://<org>.maps.arcgis.com -name-field name -status-field status -user-id-field userId -log-file log.txt -csv-file ../sample_data/workers.csv -project-id <project-id> -title-field title -contact-number-field contactNumber
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL
 2. Then the CSV file is parsed using a DictReader, which means that the order of the fields in the CSV field does not matter
 3. The workers parsed from the CSV are validated.
 4. Add the workers to the workforce project
