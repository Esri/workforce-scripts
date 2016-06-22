import logging
import sys
import requests


def post(url,data=None, files=None):
    """
    Makes a POST request with the provided url and data
    :param url: (string) The url to post to
    :param data: (dictionary) The data (if any) to send
    :return:
    """
    logging.getLogger().debug("Posting to: {}".format(url))
    response = requests.post(url,data, files=files).json()
    logging.getLogger().debug(response)
    return response

def get(url,params=None):
    """
    Makes a GET request with the provided url and parameters
    :param url: (string) The url to get
    :param params: (dictionary) The parameters to submit
    :return:
    """
    params['f']='json'
    logging.getLogger().debug("Getting: {}".format(url))
    response = requests.get(url,params).json()
    logging.getLogger().debug(response)
    return response


def get_token(org_url,username, password, expiration=60):
    """
    This gets the token needed to authenticate (using built-in security) with AGOL
    :param org_url: (string) The organizational url to use (https://yourorg.maps.arcgis.com)
    :param username: (string) The username to authenticate with (must have edit permissions)
    :param password: (string) The password to authenticate with
    :param expiration: (int) The length (in minutes) for which the token is valid
    :return:
    """
    # Build the generate token url
    url = "{}/{}".format(org_url.rstrip("/"),"sharing/rest/generateToken")
    data = {
        'username': username,
        'password': password,
        'referer': org_url,
        'f':'json',
        'expiration':expiration
    }
    # GET the token url and extract the token from the json/dict
    response = post(url,data)
    token = response["token"]
    return token


def query_feature_layer(feature_layer_url, token, where=None, oids=None, outSR=None, outFields="*"):
    """
    This queries the specified feature layer url to get features
    :param feature_layer_url: (string) The feature layer url
    :param token: (string) The token to authenticate with
    :param where: (string) The where clause to use (optional)
    :param oids: (list) The list of OBJECTIDs to query
    :param outSR: (string) The output spatial reference to use (wkid)
    :param outFields: (CSV string) The fields to return
    :return:
    """
    query_url = "{}/query".format(feature_layer_url.rstrip("/"))
    params = {
        'token': token,
        'f': 'json',
        'outFields': outFields
    }
    if where:
        params["where"] = where
    elif oids:
        params["objectIds"] = ",".format(oids)
    else:
        params["where"] = "1=1"
    if outSR:
        params["outSR"] = outSR
    response = get(query_url,params)
    return response


def get_feature_layer(feature_layer_url, token):
    """
    This gets the feature layer metadata
    :param feature_layer_url: (string) The feature layer to request
    :param token: (string) The token to authenticate with
    :return:
    """
    params = {
        'token': token,
        'f': 'json'
    }
    return get(feature_layer_url,params)


def get_assignments_feature_layer_url(org_url, token, projectId):
    """
    Gets the assignments url from the project ID
    :param org_url: (string) The organizational url where the project resides and that the token is valid for
    :param token:  (string) The authenticated token to use
    :param projectId: (string) The project ID (from AGOL)
    :return:
    """
    project_path = "{}/sharing/rest/content/items/{}/data".format(org_url, projectId)
    params = {
        "token": token,
        "f": "json",
        "referer": org_url
    }
    res = get(project_path, params)
    return res["assignments"]["url"]


def get_workers_feature_layer_url(org_url, token, projectId):
    """
    Gets the workers url from the project ID
    :param org_url: (string) The organizational url where the project resides and that the token is valid for
    :param token:  (string) The authenticated token to use
    :param projectId: (string) The project ID (from AGOL)
    :return:
    """
    project_path = "{}/sharing/rest/content/items/{}/data".format(org_url, projectId)
    params = {
        "token": token,
        "f": "json",
        "referer": org_url
    }
    res = get(project_path, params)
    return res["workers"]["url"]


def get_dispatchers_feature_layer_url(org_url, token, projectId):
    """
    Gets the dispatchers url from the project ID
    :param org_url: (string) The organizational url where the project resides and that the token is valid for
    :param token:  (string) The authenticated token to use
    :param projectId: (string) The project ID (from AGOL)
    :return:
    """
    project_path = "{}/sharing/rest/content/items/{}/data".format(org_url, projectId)
    params = {
        "token": token,
        "f": "json",
        "referer": org_url
    }
    res = get(project_path, params)
    return res["dispatchers"]["url"]


def get_location_feature_layer_url(org_url, token, projectId):
    """
    Gets the location url from the project ID
    :param org_url: (string) The organizational url where the project resides and that the token is valid for
    :param token:  (string) The authenticated token to use
    :param projectId: (string) The project ID (from AGOL)
    :return:
    """
    project_path = "{}/sharing/rest/content/items/{}/data".format(org_url, projectId)
    params = {
        "token": token,
        "f": "json",
        "referer": org_url
    }
    res = get(project_path, params)
    return res["tracks"]["url"]


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