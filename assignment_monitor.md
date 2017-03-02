# Assignment Monitor
A demo showing how completed assignments can be stored in SQLite database and pushed to a slack channel in near real-time.

## Installation

1. Install Conda or Miniconda (plus requests) and the ArcGIS API for Python package as described [here](https://developers.arcgis.com/python/guide/install-and-set-up/).
2. Clone or download this repository
3. Modify the config.ini file to use your ArcGIS online credentials, the workforce project, the slack web-hook, and the log file.

## Running it

1. Run the script as `python assignment_monitor.py`
2. Open a workforce project as a worker on an android or ios device and complete an assignment. 
3. The script polls the feature service every 5 seconds so you should see a slack notification on your designated channel within 5 seconds.

In a real-world scenario, this script can be modified to run once (not loop forever). It would be called every so often (ie. once per minute) by a task scheduler such as Windows Task Scheduler or Cron.

## What it does

1. It creates a SQLite database and the required table (if necessary)
2. It then loads into memory any GlobalID values stored in the database
3. It queries the assignment feature service of the specified workforce project to find completed assignments
4. It checks each assignment to see if it was already added to the database, if not, then it is inserted
5. If there was a newly completed assignment, some details of it are posted to the configured slack channel.
6. It then waits for 5 seconds and repeats steps 3-6 until manually stopped (CTRL-C)

Info about Slack Webhooks can be found [here](https://api.slack.com/incoming-webhooks).
