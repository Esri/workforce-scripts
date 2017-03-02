"""
A script to monitor Worforce Assignments for completion.

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


def post_to_slack(slack_webhook, assignment, project_id):
    """
    Posts a message to slack
    :param slack_webhook: (string) The url of the slack webhook
    :param assignment: (Feature) The feature to use
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
        assignment.attributes["location"],
        assignment.attributes["description"],
        assignment.attributes["notes"],
        assignment.attributes["Editor"],
        datetime.datetime.fromtimestamp(int(assignment.attributes["completedDate"])/1000).strftime("%Y-%m-%d %H:%M"),
        "http://workforce.arcgis.com/projects/{}/dispatch/assignments/{}".format(project_id,
                                                                                  assignment.attributes["OBJECTID"])
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


def query_global(db, global_id):
    """
    Query the database for global ids
    :param db: (string) the database to query
    :param global_id: (string) the id to search for
    :return: (int) number of items with matching id
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM assignments where GlobalID = ?".format(
        global_id
    ))
    count = c.fetchone()[0]
    conn.close()
    return count


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


def add_assignment_to_db(db, assignment):
    """
    Adds an assignment to the database
    :param db: (string) The database to connect to
    :param assignment: (Feature) The assignment to add
    :return:
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    params = (
        assignment.attributes["OBJECTID"],
        assignment.attributes["description"],
        assignment.attributes["status"],
        assignment.attributes["notes"],
        assignment.attributes["priority"],
        assignment.attributes["assignmentType"],
        assignment.attributes["workOrderId"],
        assignment.attributes["dueDate"],
        assignment.attributes["workerId"],
        assignment.attributes["GlobalID"],
        assignment.attributes["location"],
        assignment.attributes["declinedComment"],
        assignment.attributes["assignedDate"],
        assignment.attributes["assignmentRead"],
        assignment.attributes["inProgressDate"],
        assignment.attributes["completedDate"],
        assignment.attributes["declinedDate"],
        assignment.attributes["pausedDate"],
        assignment.attributes["dispatcherId"],
        assignment.attributes["CreationDate"],
        assignment.attributes["Creator"],
        assignment.attributes["EditDate"],
        assignment.attributes["Editor"]
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
    config.read("my_config.ini")

    logger = initialize_logging(config["LOG"]["LOGFILE"])
    initialize_db(config["DB"]["DATABASE"])

    # Authenticate and get data
    logger.info("Authenticating with ArcGIS Online...")
    gis = arcgis.gis.GIS(config["AGOL"]["ORG"], username=config["AGOL"]["USERNAME"], password=config["AGOL"]["PASSWORD"])
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
            if not assignment.attributes["GlobalID"] in processed_global_ids:
                logger.info("Adding new assignment to sqlite database...")
                processed_global_ids.append(assignment.attributes["GlobalID"])
                # append the global id to the csv file (in-case we need to restart script)
                add_assignment_to_db(config["DB"]["DATABASE"], assignment)
                # post message to slack, if configured
                if config.has_section("SLACK") and config.has_option("SLACK","WEBHOOK"):
                    logger.info("Posting assignment to slack...")
                    post_to_slack(config["SLACK"]["WEBHOOK"], assignment, config["WORKFORCE"]["PROJECT"])
        # sleep for 5 seconds before polling again
        logger.info("Sleeping for 5 seconds...")
        time.sleep(5)