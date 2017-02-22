## Import Workers from CSV

This script reads a CSV file containing the required fields to add workers (named users) to the workforce project.

Supports Python 2.7+, 3.4+

----

Consider the following CSV example table that is to be imported into Workforce:

| name     | status | title      | contactNumber | userId       | 
|----------|--------|------------|---------------|------------|
| Jane Doe | 0      | Inspector  | 123-456-7890  | jane_doe   |



Due to the various naming conventions organizations may have, this script has many options allowing the user to specify the names of each column. In addition to the authentication arguments, the script specific arguments are as follows:

- -csvFile \<csvFile\> The csv file to read
- -logFile \<logFile\> The log file to use for logging messages
- -pid \<projectId\> The workforce project ID (from AGOL)
- -nameField \<nameField\> The name of the column that stores the workers name
- -statusField \<statusField\> The name of the column that stores the workers status. Statuses should be 0.
- -userIdField \<userIdField\> The name of the column that stores the workers named user username
- -titleField \<titleField\> (optional) The name of the column that stores the workers title
- -contactNumberField \<contactNumberField\> (optional) The name of the column that stores the workers contact number

Example Usage:
```python
python create_workers_from_csv.py -u <username> -p <password> -url https://<org>.maps.arcgis.com -nameField name -statusField status -userIdField userId -logFile log.txt -csvFile ../sample_data/workers.csv -pid <project-id> -titleField title -contactNumber contactNumber
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the requried token
 2. Then the CSV file is parsed using a DictReader, which means that the order of the fields in the CSV field does not matter
 3. The workers parsed from the CSV are validated. Check to make sure they aren't in the project already as well as check that the userId is valid.
 4. Add the workers to the workforce project (worker feature layer)
 5. Add the workers to the workforce group
