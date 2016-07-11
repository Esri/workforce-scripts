## Delete Assignments

This script deletes assignments based a query or list of OBJECTIDs

Supports Python 2.7+, 3.4+

----

This script deletes assignments based a query or list of OBJECTIDs. The script uses the following parameters:

- -logFile \<logFile\> The log file to use for logging messages
- -pid \<projectId\> - The workforce project ID (from AGOL)
- -where \<where\> - The where clause to use when querying the assignments to export (Optional - Defaults to None)
- -objectIDS \<objectIDs\> - A list of OBJECTIDs to delete

**Note**

"-where" and "-objectIDs" are mutually exlusive; you can choose one method

Example Usage (OBJECTIDs):
```python
python delete_assignments.py -u username -p password -url "https://<org>.maps.arcgis.com" -pid "038a1926d2d741dc8acabefd5b2cc5d3" -logFile "../log.txt" -objectIDs 50 51
```

Example Usage (where):
```python
python delete_assignments.py -u username -p password -url "https://<org>.maps.arcgis.com" -pid "038a1926d2d741dc8acabefd5b2cc5d3" -logFile "../log.txt" -where "priority = 1"
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the requried token
 2. Then the assignment feature layer is fetched
 3. The assignments are deleted based on the supplied query or list of OBJECTIDs
