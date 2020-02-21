## Report Complete Assignments without Completed Work Orders

This script takes assignments that have been completed (status = "completed") that do not have a corresponding completed work order (Survey or Collector feature) and reports them to the user. 

A work order is defined as a feature (row in the attribute table) that corresponds to work integrated with a Workforce assignment. For example, an inspection survey may need to be completed by a field worker at each Workforce assignment.

Whether or not the user has a corresponding work order is defined by searching a particular field in the survey/collector feature layer for the value stored in the assignment's work order id.

For example, if I have an assignment with the work_order_id "6" that has status "completed", but there is not a survey that has already been submitted with the value 6 in the field I'm using to integrate the two apps, then this is an assignment that will get logged. You provide the name of that field the script searches on.

Note that an assignment will only get reported if it has a value for Work Order ID.

This script assumes a 1:1 relationship between surveys/features and assignments.

**This script requires the logged in user to be an admin, dispatcher, or to be the owner of the project**

Supports Python 3.5+

----

In addition to the authentication arguments (org, username, password), the script specific arguments are as follows:

- -project-id \<project_id\> - The workforce project ID (found in the project URL)
- -survey-id \<survey_id\> - (Optional) The portal item id for the feature layer collection associated with your Survey123 Survey. Use EITHER this parameter or `layer_url`. Defaults to `None`
- -layer-url \<layer_url\> - (Optional) The feature service URL for your Survey or Collector layer. Make sure you use the url for the feature layer rather than the feature layer collection - the url ending in `FeatureServer/number` rather than just `FeatureServer`. Use EITHER this parameter or `survey_id`. Defaults to `None`
- -field-name \<field_name\> (Optional) - The field name of the field you use to integrate with Workforce. Do not use the alias for the field name - for example, `work_id` should be provided here instead of `Work ID`. Check your Survey or Colector feature layer to find the field name. Defaults to `work_order_id`
- -log-file \<logFile\> (Optional) - The log file to use for logging messages

Example Usage:
```bash
python report_complete_assignments_without_work_orders.py -u username -p password -org https://arcgis.com -project-id faec0353ffe441e8ac5ef191083a3b58 -survey-id bc9033ba8f4c46b3ae7df0a7fd10b771 -field-name work_order_id
```

Example Usage 2:
```bash
python report_complete_assignments_without_work_orders.py -u username -p password -org https://arcgis.com -project-id faec0353ffe441e8ac5ef191083a3b58 -layer-url http://sampleserver6.arcgisonline.com/arcgis/rest/services/NapervilleShelters/FeatureServer/0 -field-name work_order_id -log-file log.txt
```

## What it does

 1. Gets workforce assignment data and survey/collector data
 2. For every assignment, if the assignment has a work order id value and has status "completed", check if there's a corresponding work order by querying the survey/collector layer on the field --field-name
 3. If a corresponding work order is not found, report the assignment to the user
