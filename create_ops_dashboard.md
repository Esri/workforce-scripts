## Create Ops Dashboard for a Workforce Project

This script takes a Workforce project and creates a corresponding Ops Dashboard for monitoring that project, either in light or dark mode.

**This script requires the logged in user to be an admin or to be the owner of the project. Version 1 Projects only **

Supports Python 3.5+

----

In addition to the authentication arguments (org, username, password), the script specific arguments are as follows:

- -project-id \<project_id\> - The workforce project ID (found in the project URL)
- -title \<title\> - Title of your new Ops Dashboard. Defaults to project title + "Dashboard"
- --light-mode \<light_mode> - Whether you want your dashboard to be in light mode. Default dashboard is in dark mode
- --clone-map \<clone_map> - Provide this parameter if you want a copy of the dispatcher webmap to be used rather than the actual webmap. Default is False
- -log-file \<logFile\> The log file to use for logging messages

Example Usage:
```bash
python create_ops_dashboard.py -u <username> -p <password> -org https://arcgis.com -project-id <project_id> --light-mode --clone-map
```

## What it does

 1. Retrieves your Workforce project
 2. If provided, saves a copy of the Workforce dispatcher webmap
 3. Clones an example Ops Dashboard for you with your Workforce project data
 4. Updates the title of the ops dashboard
 5. Shares the ops dashboard with your Workforce project group
