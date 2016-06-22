"""
    Some common functionality based on ArcREST that is useful for workforce scripting
"""
import arcrest
from arcresthelper import securityhandlerhelper
import logging
import sys


def get_security_handler(args):
    """
    Creates the security handler for the AGOL/Portal Org
    :param args: The argparser arguments object
    :return: The security handler
    """
    logger = logging.getLogger()
    securityinfo = {}
    securityinfo['security_type'] = args.security_type
    securityinfo['username'] = args.username
    securityinfo['password'] = args.password
    securityinfo['org_url'] = args.org_url
    securityinfo['proxy_url'] = args.proxy_url
    securityinfo['proxy_port'] = args.proxy_port
    securityinfo['referer_url'] = args.referer_url
    securityinfo['token_url'] = args.token_url
    securityinfo['certificatefile'] = args.certificate_file
    securityinfo['keyfile'] = args.keyfile
    securityinfo['client_id'] = args.client_id
    securityinfo['secret_id'] = args.secret_id
    # Authenticate
    logger.debug("Authenticating...")
    shh = securityhandlerhelper.securityhandlerhelper(securityinfo)
    if not shh.valid:
        logger.critical("Failed to Authenticate")
        logger.critical(shh.message)
        sys.exit(-1)
    else:
        return shh


def get_assignments_feature_layer(shh, projectId):
    """
    Gets the assignment feature layer
    :param shh: Security handler helper
    :param projectId: The id of the project
    :return: the response of the delete REST call
    """
    logger = logging.getLogger()
    logger.debug("Getting Assignments Feature Layer...")
    portal_admin = arcrest.manageorg.Administration(securityHandler=shh.securityhandler)
    project_data = portal_admin.content.getItem(itemId=projectId).itemData(f="json")
    return arcrest.agol.FeatureLayer(project_data["assignments"]["url"], securityHandler=shh.securityhandler)


def get_dispatchers_feature_layer(shh, projectId):
    """
    Gets the dispatchers feature layer
    :param shh: Security handler helper
    :param projectId: The id of the project
    :return: the response of the delete REST call
    """
    logger = logging.getLogger()
    logger.debug("Getting Dispatchers Feature Layer...")
    portal_admin = arcrest.manageorg.Administration(securityHandler=shh.securityhandler)
    project_data = portal_admin.content.getItem(itemId=projectId).itemData(f="json")
    return arcrest.agol.FeatureLayer(project_data["dispatchers"]["url"], securityHandler=shh.securityhandler)


def get_location_feature_layer(shh, projectId):
    """
    Gets the location feature layer
    :param shh: Security handler helper
    :param projectId: The id of the project
    :return: the response of the delete REST call
    """
    logger = logging.getLogger()
    logger.debug("Getting Location Feature Layer...")
    portal_admin = arcrest.manageorg.Administration(securityHandler=shh.securityhandler)
    project_data = portal_admin.content.getItem(itemId=projectId).itemData(f="json")
    return arcrest.agol.FeatureLayer(project_data["tracks"]["url"], securityHandler=shh.securityhandler)


def get_workers_feature_layer(shh, projectId):
    """
    Gets the workers feature layer
    :param shh: Security handler helper
    :param projectId: The id of the project
    :return: the response of the delete REST call
    """
    logger = logging.getLogger()
    logger.debug("Getting Workers Feature Layer...")
    portal_admin = arcrest.manageorg.Administration(securityHandler=shh.securityhandler)
    project_data = portal_admin.content.getItem(itemId=projectId).itemData(f="json")
    return arcrest.agol.FeatureLayer(project_data["workers"]["url"], securityHandler=shh.securityhandler)


def initialize_logging(logFile):
    """
    Setup the root logger to print to the console and log to file
    :param logFile: The log file to write to
    :return:
    """
    # The format for the logs
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
    rh = logging.handlers.RotatingFileHandler(logFile, mode='a', maxBytes=10485760)
    rh.setFormatter(formatter)
    rh.setLevel(logging.DEBUG)
    # Add the handlers to the root logger
    logger.addHandler(sh)
    logger.addHandler(rh)