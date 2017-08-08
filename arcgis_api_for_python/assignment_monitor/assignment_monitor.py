# -*- coding: UTF-8 -*-
"""
Copyright 2017 Esri

   Licensed under the Apache License, Version 2.0 (the "License");

   you may not use this file except in compliance with the License.

   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software

   distributed under the License is distributed on an "AS IS" BASIS,

   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

   See the License for the specific language governing permissions and

   limitations under the License.​

A script to monitor Workforce Assignments for completion.

When an assignment is completed a message is posted to slack
"""

import configparser
import sqlite3
import datetime
import logging
import logging.handlers
import sys
import time
import arcgis
import requests


def get_field_name(field_name, fl):
    """
    Attempts to get the field name (could vary based on portal/AGOL implementation)
    :param field_name: (string) The field name to get
    :param fl: (FeatureLayer) The feature layer the field should be in
    :return: (string) The field name
    """
    for field in fl.properties["fields"]:
        if field_name == field["name"]:
            return field_name
        if field_name.lower() == field["name"]:
            return field_name.lower()
        # These field names are not only lower case but also different for Portal vs AGOL
        # CreationDate
        if field_name == "CreationDate":
            return fl.properties["editFieldsInfo"]["creationDateField"]
        # EditDate
        if field_name == "EditDate":
            return fl.properties["editFieldsInfo"]["editDateField"]
        # Creator
        if field_name == "Creator":
            return fl.properties["editFieldsInfo"]["creatorField"]
        # Editor
        if field_name == "Editor":
            return fl.properties["editFieldsInfo"]["editorField"]
    else:
        logging.getLogger().critical("Field: {} does not exist".format(field_name))
        raise Exception("Field: {} does not exist".format(field_name))
    

def post_to_slack(slack_webhook, assignment, project_id, assignment_fl):
    """
    Posts a message to slack
    :param slack_webhook: (string) The url of the slack webhook
    :param assignment: (Feature) The feature to use
    :param assignment_fl: (FeatureLayer) The assignment feature layer (needed for field lookup)
    :return:
    """
    # create the message to send
    message = "Assignment Completed:\n " \
              "Location: {}\n"\
              "Description: {}\n" \
              "Notes: {}\n"\
              "Worker: {}\n"\
              "Time: {}\n" \
              "Link: {}".format(
        assignment.attributes[get_field_name("location", assignment_fl)],
        assignment.attributes[get_field_name("description", assignment_fl)],
        assignment.attributes[get_field_name("notes", assignment_fl)],
        assignment.attributes[get_field_name("Editor", assignment_fl)],
        datetime.datetime.fromtimestamp(int(assignment.attributes[get_field_name("completedDate", assignment_fl)])/1000).strftime("%Y-%m-%d %H:%M"),
        "http://workforce.arcgis.com/projects/{}/dispatch/assignments/{}".format(project_id,
                                                                                  assignment.attributes[get_field_name("OBJECTID", assignment_fl)])
    )
    logging.getLogger().info("Posting: {} to slack".format(message))
    response = requests.post(slack_webhook, json={"text": message})
    logging.getLogger().info("Status code: {}".format(response.status_code))


def initialize_logging(log_file):
    """
    Setup logging
    :param log_file: (string) The file to log to
    :return: (Logger) a logging instance
    """
    # initialize logging
    formatter = logging.Formatter("[%(asctime)s] [%(filename)30s:%(lineno)4s - %(funcName)30s()]\
             [%(threadName)5s] [%(name)10.10s] [%(levelname)8s] %(message)s")
    # Grab the root logger
    logger = logging.getLogger()
    # Set the root logger logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.DEBUG)
    # Create a handler to print to the console
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    # Create a handler to log to the specified file
    rh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10485760)
    rh.setFormatter(formatter)
    rh.setLevel(logging.DEBUG)
    # Add the handlers to the root logger
    logger.addHandler(sh)
    logger.addHandler(rh)
    return logger


def initialize_db(db):
    """
    Initializes the database and creates the table if necessary
    :param db: (string) The database to use
    :return:
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS `Assignments` ( "
              "`OBJECTID` INTEGER, "
              "`description` TEXT, "
              "`status` TEXT, "
              "`notes` TEXT, "
              "`priority` INTEGER, "
              "`assignmentType` INTEGER, "
              "`workerOrderId` TEXT, "
              "`dueDate` INTEGER, "
              "`workerId` INTEGER, "
              "`GlobalID` TEXT UNIQUE, "
              "`location` TEXT, "
              "`declinedComment` TEXT, "
              "`assignedDate` INTEGER, "
              "`assignmentRead` INTEGER, "
              "`inProgressDate` INTEGER, "
              "`completedDate` INTEGER, "
              "`declinedDate` INTEGER, "
              "`pausedDate` INTEGER, "
              "`dispatcherId` INTEGER, "
              "`CreationDate` INTEGER, "
              "`Creator` TEXT, "
              "`EditDate` INTEGER, "
              "`Editor` TEXT, "
              "PRIMARY KEY(`GlobalID`) )")
    conn.commit()
    conn.close()


def add_assignment_to_db(db, assignment, assignment_fl):
    """
    Adds an assignment to the database
    :param db: (string) The database to connect to
    :param assignment: (Feature) The assignment to add
    :param assignment_fl: (FeatureLayer) The assignment feature layer (needed for field lookup)
    :return:
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    params = (
        assignment.attributes[get_field_name("OBJECTID", assignment_fl)],
        assignment.attributes[get_field_name("description", assignment_fl)],
        assignment.attributes[get_field_name("status", assignment_fl)],
        assignment.attributes[get_field_name("notes", assignment_fl)],
        assignment.attributes[get_field_name("priority", assignment_fl)],
        assignment.attributes[get_field_name("assignmentType", assignment_fl)],
        assignment.attributes[get_field_name("workOrderId", assignment_fl)],
        assignment.attributes[get_field_name("dueDate", assignment_fl)],
        assignment.attributes[get_field_name("workerId", assignment_fl)],
        assignment.attributes[get_field_name("GlobalID", assignment_fl)],
        assignment.attributes[get_field_name("location", assignment_fl)],
        assignment.attributes[get_field_name("declinedComment", assignment_fl)],
        assignment.attributes[get_field_name("assignedDate", assignment_fl)],
        assignment.attributes[get_field_name("assignmentRead", assignment_fl)],
        assignment.attributes[get_field_name("inProgressDate", assignment_fl)],
        assignment.attributes[get_field_name("completedDate", assignment_fl)],
        assignment.attributes[get_field_name("declinedDate", assignment_fl)],
        assignment.attributes[get_field_name("pausedDate", assignment_fl)],
        assignment.attributes[get_field_name("dispatcherId", assignment_fl)],
        assignment.attributes[get_field_name("CreationDate", assignment_fl)],
        assignment.attributes[get_field_name("Creator", assignment_fl)],
        assignment.attributes[get_field_name("EditDate", assignment_fl)],
        assignment.attributes[get_field_name("Editor", assignment_fl)]
    )
    c.execute("INSERT INTO assignments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
    conn.commit()
    conn.close()


def get_global_ids(db):
    """
    Gets all global ids in the database
    :param db: (string) The database to query
    :return: List<string> The global ids in the db
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("Select GlobalID from assignments")
    global_ids = [r[0] for r in c.fetchall()]
    return global_ids


if __name__ == "__main__":
    # parse the config file
    config = configparser.ConfigParser()
    config.read("config.ini")

    logger = initialize_logging(config["LOG"]["LOGFILE"])
    initialize_db(config["DB"]["DATABASE"])

    # Authenticate and get data
    logger.info("Authenticating with ArcGIS Online...")
    gis = arcgis.gis.GIS(config["AGOL"]["ORG"], username=config["AGOL"]["USERNAME"], password=config["AGOL"]["PASSWORD"], verify_cert=False)
    logger.info("Getting project info...")
    project_data = arcgis.gis.Item(gis, config["WORKFORCE"]["PROJECT"]).get_data()
    assignment_feature_layer = arcgis.features.FeatureLayer(project_data["assignments"]["url"], gis)

    # the list of global ids that have been sent to slack already
    logger.info("Reading processed assignments from database...")
    processed_global_ids = get_global_ids(config["DB"]["DATABASE"])

    # Loop indefinitely
    while True:
        logger.info("Querying assignments...")
        assignments = assignment_feature_layer.query(where="Status=3").features
        logger.info("Processing assignments...")
        for assignment in assignments:
            if not assignment.attributes[get_field_name("GlobalID", assignment_feature_layer)] in processed_global_ids:
                logger.info("Adding new assignment to sqlite database...")
                processed_global_ids.append(assignment.attributes[get_field_name("GlobalID", assignment_feature_layer)])
                # append the global id to the csv file (in-case we need to restart script)
                add_assignment_to_db(config["DB"]["DATABASE"], assignment, assignment_feature_layer)
                # post message to slack, if configured
                if config.has_section("SLACK") and config.has_option("SLACK","WEBHOOK"):
                    logger.info("Posting assignment to slack...")
                    post_to_slack(config["SLACK"]["WEBHOOK"], assignment, config["WORKFORCE"]["PROJECT"], assignment_feature_layer)
        # sleep for 5 seconds before polling again
        logger.info("Sleeping for 5 seconds...")
        time.sleep(5)