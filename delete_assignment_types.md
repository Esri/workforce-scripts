## Delete Assignment Types

This script deletes the assignment types in a specified workforce project.

**This script requires the logged in user to be an admin or to be the owner of the project**

**This will affect existing assignments. Use with caution.**

Supports Python 2.7+, 3.4+

----

In addition to the authentication arguments, the script specific arguments are as follows:

- -logFile \<logFile\> The log file to use for logging messages
- -pid \<projectId\> - The workforce project ID (from AGOL)

Example Usage:
```python
python delete_assignment_types.py -u <username> -p <password> -url https://<org>.maps.arcgis.com -pid <project-id> -logFile log.txt
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the required token
 2. Deletes the assignment types in the workforce project (assignment feature layer)
