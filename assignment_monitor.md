# workforce-slack-demo
A demo showing how workforce assignments pushed to a slack channel

This simple script polls a feature service for changes to a feature. It queries to see if an assignment (Feature) is completed and stores the assignment in a SQLite database. For each assignment that is completed, a slack message is sent using an incoming webhook.

## Installation

1. Install Conda or Miniconda (plus requests) and the ArcGIS API for Python package as described [here](https://developers.arcgis.com/python/guide/install-and-set-up/).
2. Clone or download this repository
3. Modify the config.ini file to use your ArcGIS online credentials, the workforce project, the slack web-hook, and the log file.

## Running it

1. Run the script as `python assignment_monitor.py`
2. Open a workforce project as a worker on an android or ios device and complete an assignment. 
3. The script polls the feature service every 5 seconds so you should see a slack notification on your designated channel within 5 seconds.

Ideally, this script would run on a server. With a few modifications it could be set up as a scheduled task or cron job.
