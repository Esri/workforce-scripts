## Create Assignments From CSV

This script reads a CSV file containing the required fields to add unassigned or assigned assignments to a workforce project. Attachments can also be uploaded if the path to the file is specified in the CSV file.

Supports Python 3.5+

----

Consider the following CSV example table that is to be imported into Workforce:

| xField  | yField | Type | Location         | Dispatcher | Description      | Priority | Work Order Id | Due Date  | Attachment                           |
|---------|--------|------|------------------|------------|------------------|----------|---------------|-----------|--------------------------------------|
| -118.15 | 33.8   | Inspection    | 123 Street # 765 | aaron_username          | Test Description | high        | 1             | 4/28/2016 | ../sample_data/attachments/logo1.png |
| -118.37 | 34.086 | Inspection    | 124 Street # 765 | aaron_username         | Test Description | low        | 2             | 4/29/2016 |                                      |


Due to the various naming conventions organizations may have, this script has many options allowing the user to specify the names of each column as well as the date format. In addition to the authentication arguments, the script specific arguments are as follows:

- -csv-file \<csvFile\> The csv file to read
- -log-file \<logFile\> The log file to use for logging messages
- -project-id \<projectId\> - The workforce project ID (from AGOL)
- -x-field \<xField\> - The name of the field in the CSV file that contains the x-coordinate geometry
- -y-field \<yField\> - The name of the field in the CSV file that contains the y-coordinate geometry
- -assignment-type-field \<assignmentTypeField\> - The name of the field in the CSV file that stores the assignment type
- -location-field \<location\> - The name of the field in the CSV file that contains the location
- -dispatcher-field \<dispatcherIdField\> - The name of the field in the CSV file that contains the dispatcher username (Optional - if not provided, the authenticated user is used as the dispatcher)
- -description-field \<descriptionField\> - The name of the field in the CSV file that contains the description (Optional)
- -priority-field \<priorityField\> - The name of field in the CSV file that contains the priority (Optional)
- -work-order-id-field \<workOrderIdField\> - The name of the field in the CSV file that contains the workerOrderId (Optional)
- -due-date-field \<dueDateField\> - The name of the field in the CSV file that contains the dueDate (Optional)
- -attachment-file-field \<attachmentFileField\> - The name of the CSV file that contains the file (if any) to upload with the assignmnent (Optional)
- -date-format \<dateFormat\> - The date format to use (Optional - defaults to "%m/%d/%Y %H:%M:%S")
- -wkid \<wkid\> - The spatial reference wkid that the x and y fields are in (Optional - defaults to 4236 (GCS_WGS_1984))
- -worker-field \<workerField\> - The field in the CSV file that contains the worker username to assign the assignment to
- -timezone \<timezone-string\> - The timezone the datetimes are in (ex. 'US/Eastern', 'US/Pacific')

Example Usage:
```python
python create_assignments_from_csv.py -csv-file "../sample_data/assignments.csv" -u username -p password -org "https://<org>.maps.arcgis.com" -project-id "038a1926d2d741dc8acabefd5b2cc5d3" -x-field "xField" -y-field "yField" -assignment-type-field "Type" -location-field "Location" -description-field "Description" -priority-field "Priority" -work-order-id-field "Work Order Id" -due-date-field "Due Date" -attachment-file-field "Attachment" -wkid 102100 -log-file "../log.txt" -worker-field "Worker" -timezone "US/Eastern"
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the requried token
 2. Then the CSV file is parsed using a DictReader, which means that the order of the fields in the CSV field does not matter
 3. Next if there is not a dispatcher field supplied, the dispatcher associated with the authenticated user is used
 4. The worker for each assignment is analyzed and the worker ID is set for the assignment
 4. The assignments parsed from the CSV are validated. Check for valid dispatcherId, workerId, status, priority, assignmentType.
 5. Add the assignments to the workforce project (assignment feature layer)
 6. Add the specified attachments to the assignments
 
## Notes

ArcGIS Online stores datetimes in UTC. You can specify the timezone your datetime values are in by using the `-timezone` option. If this is not specified, the script assumes dates are in UTC.

Additionally, if the specified datetime does not have any time associated with it, the script will append 23 hours, 59 minutes, and 59 seconds to the date, so that the entire day is valid as a due date. In the user interfaces for Workforce, any datetime with 23:59:59 is displayed as the date with no time.

