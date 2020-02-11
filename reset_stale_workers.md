## Reset Status of Stale Workers

This script takes workers who have not been edited (changed their location, status, or contact info) at or after a certain date and resets their status to "not working". This allows the administrator to modify "stale" workers.

**This script requires the logged in user to be an admin or to be the owner of the project. It also requires the pendulum Python module**

Supports Python 3.5+

----

In addition to the authentication arguments (org, gis, password), the script specific arguments are as follows:

- -project-id \<project_id\> - The workforce project ID (found in the project URL)
- -cutoff-date \<cutoff_date\> - Workers who have not been edited at or after this date will have their status reset to 'Not Working'. Date should be in: MM/DD/YYYY hh:mm:ss format. For example, "02/07/2020 19:55:00"
- -timezone - (Optional) If provided, the above cutoff date variable will be assumed to be in this timezone, as opposed to UTC. Defaults to UTC. You can list available timezones by installing the pendulum module.
- -log-file \<logFile\> The log file to use for logging messages

Example Usage:
```bash
python reset_stale_workers.py -u <username> -p <password> -org https://arcgis.com -project-id <project_id>  -cutoff-date "02/07/2020 19:55:00" -timezone "US/Eastern"
```

## What it does

 1. Converts cutoff date to UTC
 2. Uses cutoff date to get all workers who are stale
 3. Updates those workers so that their status is "Not Working"
