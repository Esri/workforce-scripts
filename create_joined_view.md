## Create Joined View

This script creates a joined hosted feature layer view that combines the assignments, assignment types, workers, and dispatchers into a single layer. This allows information like the worker name to be displayed with the assignment even though the data is stored in two different layers. This script only applies to offline-enabled Workforce projects.

**This script requires the logged in user to be an admin or to be the owner of the project**

Supports Python 3.6+

----


In addition to the authentication arguments, the script specific arguments are as follows:

- -log-file \<log-file\> The log file to use for logging messages
- -project-id \<project id\> - The workforce project ID (from AGOL). This is the item ID of the Workforce feature service (also found in the web app URL "projects/{project_id}/dispatch")
- -name \<output layer name\> The name of the resulting layer (optional - a default name will be generated if not supplied)

```bash
python create_joined_view.py -org https://arcgis.com -u username -p password -project-id cc1ed9326f16474ba35679d34bb88691 -name "Example Joined View"
```

## What it does

 1. First the script uses the provided credentials to authenticate with AGOL
 2. Then it creates a joined view layer between the assignments layer and the assignment types table
 3. Then it creates a joined view layer between the assignments layer and the workers layer
 4. Then it creates a joined view layer between the assignments layer and the dispatchers table
 5. Then it joins those previously joined layers together producing the final joined layer
 
 The reason so many intermediate joined layers are created is due to limitations of the feature service which only allow a join between a max of 2 layers.

