## Delete Assignments

This script deletes assignments based a query

Supports Python 3.5+

----

This script deletes assignments based a query or list of OBJECTIDs. The script uses the following parameters:

- -log-file \<log-file\> The log file to use for logging messages
- -project-id \<project-id\> - The workforce project ID (from AGOL)
- -where \<where\> - The where clause to use when querying the assignments to export (Optional - Defaults to None)

Example Usage:
```python
python delete_assignments.py -u username -p password -url "https://<org>.maps.arcgis.com" -project-id "038a1926d2d741dc8acabefd5b2cc5d3" -logFile "../log.txt" -where "1=1"
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL or Portal
 2. Then the assignment feature layer is fetched
 3. The assignments are deleted based on the supplied where clause
