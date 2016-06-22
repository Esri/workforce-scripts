## Check the location and time that a worker completed an assignment

This script checks the location and time of when an assignment was completed against the location of the worker at that same time. It is designed to find out if workers are completing assignments without visiting the location.
It is an extension of the [Copy Assignments](copy_assignments_fs_readme.md) script in that assignments that were improperly completed are copied to a different feature service so they can be analyzed.

Supports Python 2.7+, 3.4+

----

This script relies on a JSON configuration file that maps the original field names to the field names in the target feature service. An example is shown [here](../sample_data/fieldMappings.json) The script uses the following parameters:

- -configFile \<configFile\> The json file containing the field mappings
- -logFile \<logFile\> The log file to use for logging messages
- -pid \<projectId\> - The workforce project ID (from AGOL)
- -targetFL \<targetFL\> - The full url of the target feature layer where the assignments will be copied to
- -workers \<worker1\> \<worker2\> ...\<workern\> - The specific workers to check (optional - default to all workers in project)
- -timeTol \<timeTol\> - The time tolerance to use when checking workers locations. This value is used to provide a range around the time when the assignment was completed (optional - defaults to 5 minutes)
- -distTol \<distTol\> - The distance tolerance to use when checking if a worker completed the assignment at the assignment location (optional - defaults to 100 (m)) The units are whatever the assignments feature layer uses which by default is meters.
- -minAccuracy \<minAccuracy\> - The minimum accuracy required when querying worker locations (optional - defaults to 50 (m))

Example Usage:
```python
python check_completion_location.py -configFile "../sample_data/fieldMappings.json" -u username -p password -url "https://nitro.maps.arcgis.com" -targetFL "http://services.arcgis.com/N4jtru9dctSQR53c/arcgis/rest/services/AssignmentsArchives/FeatureServer/0" -where "1=1" -pid "e2293b52beef439ca475427287969466" -log "log.txt" -worker worker_1 -timeTol 5 -distTol 100 -minAccuracy 25
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the requried token
 2. Then the assignment feature layer is fetched
 3. Next the target feature layer is fetched
 4. Then the JSON configuration file is opened and validated (checks for missing fields and that the mapped fields exist in the target feature layer)
 5. Then the worker and location feature layers are fetched
 6. For each worker
     1. Get the id of the worker
     2. The assignments are queried by the workers name/id
     3. Then the workers location is queried based on the assignment completion date +- timeTol
     4. The distance between the workers locations and the assignment are found (including the accuracy) and compared to distTol
     5. If none of the distances are smaller than distTol, then the current assignment is marked as invalid
     6. The OBJECTIDS of all invalid assignments are used to create a query
     7. The query is used to copy assignments to a different feature service (if they don't already exists there)
