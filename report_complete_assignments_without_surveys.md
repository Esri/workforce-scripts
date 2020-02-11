## Report Complete Assignments without Survey

This script takes assignments that have been completed (status = "completed") that do not have a corresponding completed survey and reports them to the user. 

Whether or not the user has a corresponding survey is defined by searching a particular field in the survey data for the value stored in the assignment's work order id.

For example, if I have an assignment with the work_order_id "6" that has status "completed", but there is not a survey that has already been submitted with the value 6 in the field I'm using to integrate the two apps, then this is an assignment that will get logged. You provide the name of that field the script searches on.

This script assumes a 1:1 relationship between surveys and assignments.

**This script requires the logged in user to be an admin or to be the owner of the project**

Supports Python 3.5+

----

In addition to the authentication arguments (org, gis, password), the script specific arguments are as follows:

- -project-id \<project_id\> - The workforce project ID (found in the project URL)
- -survey-id \<survey_id\> - The portal item id for the feature layer collection associated with your Survey123 Survey
- -survey-field-name \<survey_field_name\> (Optional) - The field name of the field you use to integrate with Workforce. Do not use the alias for the field name - for example, `work_id` should be provided here instead of `Work ID`. Check your Survey feature layer to find the field name. Defaults to `work_order_id`
- -log-file \<logFile\> (Optional) - The log file to use for logging messages

Example Usage:
```bash
python report_incomplete_assignments_with_surveys.py -u <username> -p <password> -org https://arcgis.com -project-id faec0353ffe441e8ac5ef191083a3b58 -survey-id bc9033ba8f4c46b3ae7df0a7fd10b771 -survey-field-name work_order_id --close-assignments
```

## What it does

 1. Gets workforce assignment data and survey data
 2. For every assignment, if the assignment has a work order id value and has status "completed", check if there's a corresponding survey by querying the survey layer on the field -survey-field-name
 3. If a corresponding survey is not found, report the assignment to the user
