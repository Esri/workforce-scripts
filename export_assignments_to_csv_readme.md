## Export Assignments to CSV

This script exports assignments based on a query to a CSV file

Supports Python 3.5+. Note that this script requires the `arrow` package, which must be installed separately.

----

This script queries the assignment feature layer and exports the results to a CSV file. The script uses the following parameters:

- -log-file \<log-file\> The log file to use for logging messages
- -project-id \<project-id\> - The workforce project ID (from AGOL)
- -csv-file \<csv\> - The csv file to write the results to
- -where \<where\> - The where clause to use when querying the assignments to export (Optional - Defaults to '1=1')
- -date-format \<date-format\> - The date format to use in the exported CSV file
- -timezone \<timezone\> - The timezone to convert the dates to

Example Usage:
```basg
python export_assignments_to_csv.py -csv-file "../exported_assignments.csv" -u username -p password -org "https://<org>.maps.arcgis.com" -project-id "038a1926d2d741dc8acabefd5b2cc5d3" -log-file "../log.txt" -where "status=1" -date-format "%m/%d/%Y %H:%M:%S" -timezone "US/Eastern"
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL or Portal
 2. The assignments are queried
 3. The assignments are written to a CSV file
  1. The date values are formatted (Dates are stored in AGOL as unix timestamps (UTC time)
  2. The geometry values (x,y) are assigned as attributes
  3. A dictionary writer is used to write the the attributes to a csv file
 
## Notes

 ArcGIS Online stores datetimes in UTC. You can specify the timezone your datetime values should be exported in by using the `-timezone` option. If this is not specified, the script assumes dates are in UTC.
