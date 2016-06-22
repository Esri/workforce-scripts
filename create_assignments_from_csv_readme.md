## Create Assignments From CSV

This script reads a CSV file containing the required fields to add unassigned assignments to a workforce project. Attachments can also be uploaded if the path to the file is specified in the CSV file.

Supports Python 2.7+, 3.4+

----

Consider the following CSV example table that is to be imported into Workforce:

| xField  | yField | Type | Location         | Dispatcher | Description      | Priority | Work Order Id | Due Date  | Attachment                           |
|---------|--------|------|------------------|------------|------------------|----------|---------------|-----------|--------------------------------------|
| -118.15 | 33.8   | 1    | 123 Street # 765 | 1          | Test Description | 4        | 1             | 4/28/2016 | ../sample_data/attachments/logo1.png |
| -118.37 | 34.086 | 2    | 124 Street # 765 | 2          | Test Description | 3        | 2             | 4/29/2016 |                                      |


Due to the various naming conventions organizations may have, this script has many options allowing the user to specify the names of each column as well as the date format. In addition to the authentication arguments, the script specific arguments are as follows:

- -csvFile \<csvFile\> The csv file to read
- -logFile \<logFile\> The log file to use for logging messages
- -pid \<projectId\> - The workforce project ID (from AGOL)
- -xField \<xField\> - The name of the field in the CSV file that contains the x-coordinate geometry
- -yField \<yField\> - The name of the field in the CSV file that contains the y-coordinate geometry
- -assignmentTypeField \<assignmentTypeField\> - The name of the field in the CSV file that stores the assignment type
- -locationField \<location\> - The name of the field in the CSV file that contains the location 
- -dispatcherIdField \<dispatcherIdField\> - The name of the field in the CSV file that contains the dispatcher ID (Optional - if not provided, the authenticated user is used as the dispatcher)
- -descriptionField \<descriptionField\> - The name of the field in the CSV file that contains the description (Optional)
- -priorityField \<priorityField\> - The name of field in the CSV file that contains the priority (Optional)
- -workOrderIdField \<workOrderIdField\> - The name of the field in the CSV file that contains the workerOrderId (Optional)
- -dueDateField \<dueDateField\> - The name of the field in the CSV file that contains the dueDate (Optional)
- -attachmentFileField \<attachmentFileField\> - The name of the CSV file that contains the file (if any) to upload with the assignmnent (Optional)
- -dateFormat \<dateFormat\> - The date format to use (Optional - defaults to "%m/%d/%Y")
- -wkid \<wkid\> - The spatial reference wkid that the x and y fields are in (Optional - defaults to 4236 (GCS_WGS_1984))

Example Usage:
```python
python create_assignments_form_csv.py -csvFile "../sample_data/assignments.csv" -u username -p password -url "https://nitro.maps.arcgis.com" -pid "038a1926d2d741dc8acabefd5b2cc5d3" -xField "xField" -yField "yField" -assignmentTypeField "Type" -locationField "Location" -descriptionField "Description" -priorityField "Priority" -workOrderIdField "Work Order Id" -dueDateField "Due Date" -attachmentFileField "Attachment" -wkid 102100 -logFile "../log.txt"
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL to get the requried token
 2. Then the CSV file is parsed using a DictReader, which means that the order of the fields in the CSV field does not matter
 3. Next if there is not a dispatcher field supplied, the dispatcher ID associated with the authenticated user is found
 4. The assignments parsed from the CSV are validated. Check for valid dispatcherId, status, priority, assignmentType.
 5. Add the assignments to the workforce project (assignment feature layer)
 6. Add the specified attachments to the assignments
