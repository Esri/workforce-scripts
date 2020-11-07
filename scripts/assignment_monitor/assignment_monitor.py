# -*- coding: UTF-8 -*-
"""
Copyright 2020 Esri

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
import logging
import logging.handlers
import sys
import time
import datetime
from arcgis.apps import workforce
from arcgis.gis import GIS
import requests
import inspect
import yagmail


def post_to_slack(slack_webhook, assignment):
    """
    Posts a message to slack
    :param slack_webhook: (string) The url of the slack webhook
    :param assignment: (Feature) The feature to use
    :return:
    """
    # create the message to send
    message = """
    *Assignment Completed*:
    *Assignment Type:* {}
    *Location*: {}
    *Description*: {}
    *Notes*: {}
    *Worker*: {}
    *Time*: {}
    *Link*: {}
    """.format(
        assignment.assignment_type.name,
        assignment.location,
        assignment.description,
        assignment.notes,
        assignment.worker.name,
        assignment.completed_date.strftime("%Y-%m-%d %H:%M"),
        "https://workforce.arcgis.com/projects/{}/dispatch/assignments/{}".format(
            assignment.project.id,
            assignment.object_id
        )
    )
    logging.getLogger().info("Posting: {} to slack".format(inspect.cleandoc(message)))
    response = requests.post(slack_webhook, json={"text": inspect.cleandoc(message)})
    logging.getLogger().info("Status code: {}".format(response.status_code))


def initialize_logging(log_file=None):
    """
    Setup logging
    :param log_file: (string) The file to log to
    :return: (Logger) a logging instance
    """
    # initialize logging
    formatter = logging.Formatter(
        "[%(asctime)s] [%(filename)30s:%(lineno)4s - %(funcName)30s()][%(threadName)5s] [%(name)10.10s] [%(levelname)8s] %(message)s")
    # Grab the root logger
    logger = logging.getLogger()
    # Set the root logger logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.DEBUG)
    # Create a handler to print to the console
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    # Create a handler to log to the specified file
    if log_file:
        rh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10485760)
        rh.setFormatter(formatter)
        rh.setLevel(logging.DEBUG)
        logger.addHandler(rh)
    # Add the handlers to the root logger
    logger.addHandler(sh)
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
              "`GlobalID` TEXT UNIQUE, "
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
        assignment.global_id,
    )
    c.execute("INSERT INTO assignments VALUES (?)",
              params)
    conn.commit()
    conn.close()


def is_assignment_processed(db, assignment):
    """
    Gets all global ids in the database
    :param db: (string) The database to query
    :return: List<string> The global ids in the db
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("Select GlobalID from assignments where GlobalID=?", (assignment.global_id,))
    global_ids = [r[0] for r in c.fetchall()]
    return bool(global_ids)


def send_email(gmail_username, recipient_emails, assignment):
    client = yagmail.SMTP(gmail_username)
    recipient_emails = recipient_emails.replace(" ", "").split(",")
    subject = str(assignment) + " has been completed"
    body = """
    Assignment Completed:
    Assignment Type: {}
    Location: {}
    Description: {}
    Notes: {}
    Worker: {}
    Time: {}
    Link: {}
    """.format(
        assignment.assignment_type.name,
        assignment.location,
        assignment.description,
        assignment.notes,
        assignment.worker.name,
        assignment.completed_date.strftime("%Y-%m-%d %H:%M"),
        "https://workforce.arcgis.com/projects/{}/dispatch/assignments/{}".format(
            assignment.project.id,
            assignment.object_id
        )
    )
    client.send(to=recipient_emails, subject=subject, contents=body)


if __name__ == "__main__":
    # parse the config file
    config = configparser.ConfigParser()
    config.read("config.ini")

    logger = initialize_logging(config["LOG"]["LOGFILE"])
    initialize_db(config["DB"]["DATABASE"])

    # Authenticate and get data
    logger.info("Authenticating with ArcGIS Online...")
    gis = GIS(config["AGOL"]["ORG"],
              username=config["AGOL"]["USERNAME"],
              password=config["AGOL"]["PASSWORD"],
              verify_cert=False)

    logger.info("Getting project info...")
    project = workforce.Project(gis.content.get(config["WORKFORCE"]["PROJECT"]))

    # Loop indefinitely
    while True:
        logger.info("Querying assignments...")
        timestamp_last_minute = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1)).strftime(
            "%Y-%m-%d %H:%M:%S")
        assignments = project.assignments.search("{} = 3 AND {} >= timestamp '{}'".format(
            project._assignment_schema.status,
            project._assignment_schema.completed_date,
            timestamp_last_minute
        ))
        logger.info("Processing assignments...")
        for assignment in assignments:
            if not is_assignment_processed(config["DB"]["DATABASE"], assignment):
                logger.info("Adding new assignment to sqlite database...")
                # append the global id to the csv file (in-case we need to restart script)
                add_assignment_to_db(config["DB"]["DATABASE"], assignment)
                if config.has_section("EMAIL") and config.has_option("EMAIL", "GMAIL_USERNAME") and config["EMAIL"]["SEND_EMAIL"]:
                    send_email(config["EMAIL"]["GMAIL_USERNAME"], config["EMAIL"]["RECIPIENT_EMAILS"], assignment)
                    logger.info("Email sent")
                # post message to slack, if configured
                if config.has_section("SLACK") and config.has_option("SLACK", "WEBHOOK"):
                    logger.info("Posting assignment to slack...")
                    post_to_slack(config["SLACK"]["WEBHOOK"], assignment)
        # sleep for 5 seconds before polling again
        logger.info("Sleeping for 5 seconds...")
        time.sleep(5)
