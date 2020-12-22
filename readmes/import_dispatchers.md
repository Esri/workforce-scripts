## Import Dispatchers from CSV

This script reads a CSV file containing the required fields to add dispatchers (named users) to the workforce project.

**This script requires the logged in user to be an admin or to be the owner of the project**

Supports Python 3.5+

----

Consider the following CSV example table that is to be imported into Workforce:

| name      | contactNummber | userId       |
|-----------|---------------|------------|
| Jane Doe  | 123-456-7890  | jane_doe   |



Due to the various naming conventions organizations may have, this script has many options allowing the user to specify the names of each column. In addition to the authentication arguments, the script specific arguments are as follows:

- -csv-file \<csvFile\> The csv file to read
- -log-file \<logFile\> The log file to use for logging messages
- -project-id \<projectId\> The workforce project ID (from AGOL)
- -name-field \<nameField\> The name of the column that stores the dispatchers name
- -user-id-field \<userIdField\> The name of the column that stores the dispatchers named user username
- -contact-number-field \<contactNumberField\> (optional) The name of the column that stores the dispatchers contact number

Example Usage:
```bash
python import_dispatchers.py -u <username> -p <password> -org https://<org>.maps.arcgis.com -name-field name -user-id-field userId -log-file log.txt -csv-file ../sample_data/dispatchers.csv -project-id <project-id> -contact-number-field contactNumber
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL
 2. Then the CSV file is parsed using a DictReader, which means that the order of the fields in the CSV field does not matter
 3. The dispatchers parsed from the CSV are validated.
 4. Add the dispatchers to the workforce project
