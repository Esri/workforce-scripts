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

   This sample logs completed assignments without a corresponding survey / collector feature
"""

import argparse
import logging
import logging.handlers
import sys
import traceback
from arcgis.apps import workforce
from arcgis.gis import GIS
from arcgis.features import FeatureLayer


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


def main(arguments):
	# Initialize logging
	logger = initialize_logging(arguments.log_file)
	
	# Create the GIS
	logger.info("Authenticating...")
	
	# First step is to get authenticate and get a valid token
	gis = GIS(arguments.org_url,
			  username=arguments.username,
			  password=arguments.password,
			  verify_cert=not arguments.skip_ssl_verification)
	logger.info("Getting workforce project")
	
	# Get the workforce project
	item = gis.content.get(arguments.project_id)
	try:
		project = workforce.Project(item)
	except Exception as e:
		logger.info(e)
		logger.info("Invalid project id")
		sys.exit(0)
		
	layer = None
	# Get Survey or Collector Feature Layer
	if arguments.survey_id and arguments.layer_url:
		logger.info("Please try again with either survey id or layer url provided, not both")
		sys.exit(0)
	elif arguments.survey_id:
		survey_item = gis.content.get(arguments.survey_id)
		if survey_item:
			layer = survey_item.layers[0]
	elif arguments.layer_url:
		layer = FeatureLayer(arguments.layer_url)
	else:
		logger.info("Please provide either a portal id for your survey feature layer or a feature service URL for your survey/collector layer")
		sys.exit(0)
	
	# Check if layer exists
	try:
		json = layer._lyr_json
	except Exception as e:
		logger.info(e)
		logger.info("Layer could not be found based on given input. Please check your parameters again. Exiting the script")
		sys.exit(0)
	
	# Updating Assignments
	logger.info("Querying assignments")
	assignments = project.assignments.search()
	for assignment in assignments:
		if assignment.status == "completed" and assignment.work_order_id:
			where = f"{arguments.field_name} = '{assignment.work_order_id}'"
			if layer.query(where=where, return_count_only=True) == 0:
				logger.info(f"Potential Assignment without corresponding work order: {str(assignment)} with OBJECTID {assignment.object_id}")
				if gis.properties["isPortal"]:
					portal_url = gis.properties['portalHostname']
					logger.info(f"Assignment Link: {portal_url}/apps/workforce/#/projects/{arguments.project_id}/dispatch/assignments/{assignment.object_id}")
				else:
					logger.info(f"Assignment Link: https://workforce.arcgis.com/projects/{arguments.project_id}/dispatch/assignments/{assignment.object_id}")
	logger.info("Completed!")


if __name__ == "__main__":
	# Get all of the commandline arguments
	parser = argparse.ArgumentParser("Report completed assignments without work orders")
	parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
	parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
	parser.add_argument('-org', dest='org_url', help="The url of the org/portal to use", required=True)
	# Parameters for workforce
	parser.add_argument('-project-id', dest='project_id', help="The id of the Workforce project", required=True)
	parser.add_argument('-survey-id', dest='survey_id',
						help="The portal item id for the feature layer collection associated with your Survey123 Survey",
						default=None)
	parser.add_argument('-layer-url', dest='layer_url',
						help="The feature service URL for your Survey or Collector layer",
						default=None)
	parser.add_argument('-field-name', dest='field_name', default="work_order_id",
						help="The field name within the Survey or Collector layer you use to integrate with Workforce. Use actual field name, not alias. Default is work_order_id")
	parser.add_argument('-log-file', dest='log_file', help='The log file to use')
	parser.add_argument('--skip-ssl-verification', dest='skip_ssl_verification', action='store_true',
						help="Verify the SSL Certificate of the server")
	args = parser.parse_args()
	try:
		main(args)
	except Exception as e:
		logging.getLogger().critical("Exception detected, script exiting")
		logging.getLogger().critical(e)
		logging.getLogger().critical(traceback.format_exc().replace("\n", " | "))
