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

   This sample creates a default ops dashboard based on inputs
"""

import argparse
import logging
import logging.handlers
import sys
import traceback
from arcgis.apps import workforce
from arcgis.gis import GIS


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
	
	# Get your workforce project
	item = gis.content.get(arguments.project_id)
	try:
		project = workforce.Project(item)
	except Exception as e:
		logger.info(e)
		logger.info("Invalid project id")
		sys.exit(0)
	
	# Clone dispatcher map if desired by user
	if not arguments.use_dispatcher_webmap:
		logger.info("Saving copy of dispatcher webmap")
		map_id = project.dispatcher_webmap.save(item_properties={"title": project.title + " Dashboard Map", "tags": [], "snippet": "Dashboard Map"}).id
	else:
		map_id = project.dispatcher_web_map_id
		
	# Get example ops dashboard from workforce_scripts, map to your project
	logger.info("Getting example dashboard")
	if arguments.light_mode:
		item = gis.content.get('1cbac058ce1b4a008a6baa0f3cfd506a')
		item_mapping = {'2249c41dcec34b91b3990074ed8c8ffc': project.assignments_item.id,
						'6afe245f9f3f48e8884dc7e691841973': project.workers_item.id,
						 'e605c140ecf14cccaf1e7b3bcb4b1710': map_id}
	else:
		item = gis.content.get("af7cd356c21a4ded87d8cdd452fd8be3")
		item_mapping = {'377b2b2014f24b0ab9b053d9b2fed113': project.assignments_item.id,
						'e1904f5c56484163a021155f447adf34': project.workers_item.id,
						'bb7d2b495ecc4ea7810b28f16ef71cba': map_id}
	
	# Create new dashboard using your project
	logger.info("Creating dashboard")
	cloned_items = gis.content.clone_items([item], item_mapping=item_mapping)
	if len(cloned_items) == 0:
		logger.info("You have already cloned a dashboard of this name! Check your item content and if necessary, set a title")
		sys.exit(0)
	
	# Save new name and share to group
	logger.info("Updating title and sharing to project group")
	if arguments.title:
		new_title = arguments.title
	else:
		new_title = project.title + " Dashboard"
	cloned_items[0].update(item_properties={"title": new_title}, thumbnail="https://www.arcgis.com/apps/opsdashboard/assets/images/no-dashboard-thumb-84c2afc9d73774823c7865b4cc776b9b.png")
	cloned_items[0].share(groups=[project.group])
	logger.info("Completed")


if __name__ == "__main__":
	# Get all of the commandline arguments
	parser = argparse.ArgumentParser("Create an Ops dashboard given a Workforce project")
	parser.add_argument('-u', dest='username', help="The username to authenticate with", required=True)
	parser.add_argument('-p', dest='password', help="The password to authenticate with", required=True)
	parser.add_argument('-org', dest='org_url', help="The url of the org/portal to use", required=True)
	# Parameters for workforce
	parser.add_argument('-project-id', dest='project_id', help="The id of the Workforce project", required=True)
	parser.add_argument('-title', dest='title', help="Title of your new Ops Dashboard. Defaults to project title", required=False)
	parser.add_argument('--light-mode', dest='light_mode', action='store_true', help="Light mode dashboard. Default is dark mode")
	parser.add_argument('--use-dispatcher-webmap', dest='use_dispatcher_webmap', action='store_true', default=False,
						help="Use the actual dispatcher webmap in your dashboard as opposed to a copy of the webmap")
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
