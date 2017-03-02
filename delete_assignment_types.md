## Create Assignment Types From CSV

This script reads a CSV file containing the assignment types to add to the workforce project.

**This script requires the logged in user to be an admin or to be the owner of the project**

Supports Python 2.7+, 3.4+

----

Consider the following CSV example that is to be imported into Workforce:

`Installation, Removal, Renovation, Demolition`


In addition to the authentication arguments, the script specific arguments are as follows:

- -csvFile \<csvFile\> The csv file to read
- -logFile \<logFile\> The log file to use for logging messages
- -pid \<projectId\> - The workforce project ID (from AGOL)

Example Usage:
```python
python create_assignment_types.py -u <username> -p <password> -url https://<org>.maps.arcgis.com -pid <project-id> -csvFile ../sample_data/assignment_types.csv -logFile log.txt
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the required token
 2. Then the CSV file is parsed.
 3. The assignment types parsed from the CSV are validated. We don't want any duplicates.
 4. Add the assignment types to the workforce project (assignment feature layer)
