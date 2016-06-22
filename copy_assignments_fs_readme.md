## Copy assignments to another feature class

This script copies assignments from the workforce project to another feature service

Supports Python 2.7+, 3.4+

----

This script relies on a JSON configuration file that maps the original field names to the field names in the target feature service (fields may vary, change this config file as needed). An example is shown [here](../sample_data/fieldMappings.json) The script uses the following parameters:

- -configFile \<configFile\> The json file containing the field mappings
- -logFile \<logFile\> The log file to use for logging messages
- -pid \<projectId\> - The workforce project ID (from AGOL)
- -targetFL \<targetFL\> - The full url of the target feature layer where the assignments will be copied to
- -where \<where\> - The where clause to use when querying the assignments to copy (Optional - Defaults to '1=1')

Example Usage:
```python
python copy_assignments_fs.py -configFile "../sample_data/archive_config.json" -u username -p password -url "https://nitro.maps.arcgis.com" -targetFL "http://services.arcgis.com/N4jtru9dctSQR53c/arcgis/rest/services/AssignmentsArchives/FeatureServer/0" -where "1=1" -pid "038a1926d2d741dc8acabefd5b2cc5d3" -log "log.txt"
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the requried token
 2. Then the assignment feature layer is fetched
 3. Next the target feature layer is fetched
 4. Then the JSON configuration file is opened and validated (checks for missing fields and that the mapped fields exist in the target feature layer)
 5. The assignments are queried
 6. The features in the target feature layer are queried
 7. Assignments not already in the target feature layer are determined
 8. The assignments are added to the target feature layer
