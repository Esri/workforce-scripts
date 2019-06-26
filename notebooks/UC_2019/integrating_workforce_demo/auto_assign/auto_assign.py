# -*- coding: UTF-8 -*-
"""
Copyright 2019 Esri
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
import datetime
from arcgis.apps import workforce
from arcgis.gis import GIS
from arcgis.network import RouteLayer
import requests
import inspect


def assign_worker(assignment):
    project = assignment.project
    workers = assignment.project.workers.search(where="status in (1,2)")
    for worker in workers:
        distance = calculate_route_distance(worker.geometry, assignment.geometry, project)
        worker.feature.attributes["score"] = distance
    workers = sorted(workers, key=lambda x: x.feature.attributes["score"])
    if len(workers) > 0:
        assignment.update(worker=workers[0], status="assigned", assigned_date=datetime.datetime.now())


def calculate_route_distance(p1, p2, project):
    route_layer = RouteLayer('http://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World',
                             gis=project.gis)
    if 'spatialReference' not in p1:
        p1 = {'x': p1['x'], 'y': p1['y'], 'spatialReference': {'wkid': 102100}}
    if 'spatialReference' not in p2:
        p2 = {'x': p2['x'], 'y': p2['y'], 'spatialReference': {'wkid': 102100}}
    stops = {
        'features': [
            {'geometry': p1, 'attributes': {'Name': 'start'}},
            {'geometry': p2, 'attributes': {'Name': 'end'}}
        ]
    }
    try:
        route = route_layer.solve(stops, out_sr=102100, directions_length_units="esriNAUMeters")
        return route["directions"][0]["summary"]["totalLength"]
    except Exception as e:
        return sys.maxsize


def post_to_slack(slack_webhook, assignment):
    """
    Posts a message to slack
    :param slack_webhook: (string) The url of the slack webhook
    :param assignment: (Feature) The feature to use
    :return:
    """
    # create the message to send
    message = f"""
    *Assignment Assigned*:
    *Assignment Type:* {assignment.assignment_type.name}
    *Location*: {assignment.location}
    *Description*: {assignment.description}
    *Worker*: {assignment.worker.name}
    *Created*: {assignment.creation_date.strftime("%Y-%m-%d %H:%M")}
    *Link*: {f"https://workforce.arcgis.com/projects/{assignment.project.id}/dispatch/assignments/{assignment.object_id}"}
    """
    logging.getLogger().info("Posting: {} to slack".format(inspect.cleandoc(message)))
    response = requests.post(slack_webhook, json={"text": inspect.cleandoc(message)})
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


if __name__ == "__main__":
    # parse the config file
    config = configparser.ConfigParser()
    config.read("my_config.ini")

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

    logger.info("Querying assignments...")
    timestamp_last_minute = (datetime.datetime.utcnow() - datetime.timedelta(minutes=60)).strftime(
        "%Y-%m-%d %H:%M:%S")
    assignments = project.assignments.search("{} = 0 AND {} >= timestamp '{}'".format(
        project._assignment_schema.status,
        project._assignment_schema.creation_date,
        timestamp_last_minute
    ))
    logger.info("Processing assignments...")
    for assignment in assignments:
        if not is_assignment_processed(config["DB"]["DATABASE"], assignment):
            logger.info("Assigning new assignment...")
            assign_worker(assignment)
            logger.info("Adding new assignment to sqlite database...")
            # append the global id to the csv file (in-case we need to restart script)
            add_assignment_to_db(config["DB"]["DATABASE"], assignment)
            # post message to slack, if configured
            if config.has_section("SLACK") and config.has_option("SLACK", "WEBHOOK"):
                logger.info("Posting assignment to slack...")
                post_to_slack(config["SLACK"]["WEBHOOK"], assignment)
