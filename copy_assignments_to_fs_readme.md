## Copy assignments to another feature class

This script copies assignments from the workforce project to another feature service

Supports Python 3.5+

----

This script relies on a JSON configuration file that maps the original field names to the field names in the target feature service (fields may vary, change this config file as needed). An example is shown [here.](sample_data/fieldMappings.json) **The target OBJECTID and GlobalID fields must have different names such as Original_OBJECTID and Original_GlobalID, as these fields are auto-generated when creating a new feature. If you use a mapping like (OBJECTID => OBJECTID, GlobalID => GlobalID) rather than (OBJECTID => Original_OBJECTID, GlobalID => Original_Global_ID), then you may see duplicate items copied over, since the source GlobalID and OBJECTID values will not be stored in the target features. The OBJECTID field in the target feature layer should be an Integer, the GlobalID field in the target feature layer should be String.**

The script uses the following parameters:

- -config-file \<configFile\> The json file containing the field mappings
- -log-file \<logFile\> The log file to use for logging messages
- -project-id \<projectId\> - The workforce project ID (from AGOL)
- -target-fl \<targetFL\> - The full url of the target feature layer where the assignments will be copied to
- -where \<where\> - The where clause to use when querying the assignments to copy (Optional - Defaults to '1=1')
- --copy-attachments - A flag that when set will copy the attachments to the target feature layer (this can be slow if there are a lot attachments or features)

Example Usage:
```python
python copy_assignments_to_fs.py -config-file "../sample_data/fieldMappings.json" -u username -p password -org "https://<org>.maps.arcgis.com" -target-fl "http://services.arcgis.com/<server>/arcgis/rest/services/AssignmentsArchives/FeatureServer/0" -where "1=1" -project-id "038a1926d2d741dc8acabefd5b2cc5d3" -log-file "log.txt" --copy-attachments
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the requried token
 2. Then the project is fetched
 3. Then the JSON configuration file is opened
 4. The assignments are queried
 5. The features in the target feature layer are queried
 6. Assignments not already in the target feature layer are determined
 7. The assignments are added to the target feature layer
 8. Attachments are copied to the target feature layer (optional)
