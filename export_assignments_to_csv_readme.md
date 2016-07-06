## Export Assignments to CSV

This script exports assignments based on a query to a CSV file

Supports Python 2.7+, 3.4+

----

This script queries the assignment feature layer and exports the results to a CSV file. The script uses the following parameters:

- -logFile \<logFile\> The log file to use for logging messages
- -pid \<projectId\> - The workforce project ID (from AGOL)
- -outCSV \<outCSV\> - The csv file to write the results to
- -outSR \<outSR\> - The spatial reference to export the points in (Optional - Defaults to the SR of the feature service/layer)
- -where \<where\> - The where clause to use when querying the assignments to export (Optional - Defaults to '1=1')
- -dateFormat \<dateFormat\> - The date format to use in the exported CSV file

Example Usage:
```python
python export_assignments_to_csv.py -outCSV "../exported_assignments.csv" -u username -p password -url "https://<org>.maps.arcgis.com" -pid "038a1926d2d741dc8acabefd5b2cc5d3" -logFile "../log.txt" -outSR 10200 -where "status=1" -dateFormat "%m/%d/%Y"
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the requried token
 2. Then the assignment feature layer is fetched
 3. Next the target feature layer is fetched
 4. The assignments are queried
 5. The assignments are written to a CSV file 
  1. The date values are formatted (Dates are stored in AGOL as unix timestamps (UTC time)
  2. The geometry values (x,y) are assigned as attributes
  3. A dictionary writer is used to write the the attributes to a csv file
  
## Notes
 
 The output dates are in UTC time so if you want to make them be localized, you will have to use a third party library that handles historical timezones and daylight saving time. See [PYTZ](https://pypi.python.org/pypi/pytz?)
