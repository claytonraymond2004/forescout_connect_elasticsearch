import json
import urllib.request
import base64
import re
import fnmatch
from datetime import datetime

# Hold response to Forescout EyeExtend Connect
# Like the action response, the response object must have a "succeeded" field to denote success. It can also optionally have
# a "result_msg" field to display a custom test result message.
response = {}

# Get Forescout OIM Web API Details (We connect to OIM to get data)
forescout_url = params["connect_elasticsearch_forescout_url"]
forescout_jwt_token = params["connect_authorization_token"]

# Get Elasticsearch API Details (To send data to)
elastic_url = params["connect_elasticsearch_url"]
elastic_index = params["connect_elasticsearch_index"]
if params["connect_elasticsearch_send_host_data_index_override"] != "null":
    elastic_index = params["connect_elasticsearch_send_host_data_index_override"]
elastic_username = params["connect_elasticsearch_username"]
elastic_password = params["connect_elasticsearch_password"]
elastic_apikey = params["connect_elasticsearch_apikey"] == "true"

# Get parameter details from action dialog
host_ip = params["ip"] # Host IP address
send_all_data = params["connect_elasticsearch_send_host_data_allfields"] == "true" # If all data should be included from host
specified_data = params["connect_elasticsearch_send_host_data_hostfields"] # or specific parsed version
host_data = {} # don't have host data yet

# Create request to get host data from Forescout
forescout_headers = {"Authorization": forescout_jwt_token}
forescout_request = urllib.request.Request(forescout_url + "/api/hosts/ip/" + host_ip, headers=forescout_headers)

logging.debug("Preparing to get host data from Forescout Web API")

try:
    # Make API request to Forescout Web API For host
    forescout_resp = urllib.request.urlopen(forescout_request, context=ssl_context) # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
    if forescout_resp.getcode() == 200:
        logging.debug("Got data from Forescout Web API")
        # Load response data
        host_data = json.loads(forescout_resp.read().decode('utf-8'))

        # Process host data with respect to EyeExtend Connect Send Data action specification
        logging.debug("Preparing elasticsearch payload")
        elastic_payload = {}
        if(send_all_data):
            # If send all is checked, we send all, not need for extra formatting
            elastic_payload = host_data["host"]
            elastic_payload["time"] = datetime.now().isoformat()
        else: 
            # Add IP and mac field to data and setup for fields data
            elastic_payload["time"] = datetime.now().isoformat()
            elastic_payload["ip"] = host_data["host"]["ip"]
            elastic_payload["mac"] = host_data["host"]["mac"]
            elastic_payload["id"] = host_data["host"]["id"]
            elastic_payload["fields"] = {}

            # Take user input and extract requested fields and alias name
            specified_fields = specified_data.split(",") # split the stirng format at commas

            # Take each field specification and get the data form the host_data
            for field_token in specified_fields:
                re_match = re.match("(?P<field_name>.*)\((?P<alias_name>.*)\)", field_token) # Regex to break up the format
                field_name = re_match.group('field_name')
                alias_name = re_match.group('alias_name')

                # Check if there is a wildcard character in the field speccification
                if '*' in field_name:
                    # Make sure only 1 wildcard character entered
                    if field_name.count("*") > 1 or alias_name.count("*") > 1:
                        raise Exception("Only 1 wildcard (*) character allowed in a field or alias specification")
                    elif alias_name.count("*") < 1:
                        raise Exception("Wildcard (*) character not expressed in alias field -- must be provided to preserve uniqueness of findings in output.")
                    else:
                        # convert wildcard to regex and make a token for what the wildcard matches
                        dynamic_match_re = field_name.replace("*", "(?P<token>.*)")
                        # search through all keys looking for any matches
                        for key in host_data["host"]["fields"].keys():
                            match = re.match(dynamic_match_re, key)
                            if match:
                                elastic_payload["fields"][alias_name.replace("*", match.group("token"))] = host_data["host"]["fields"][key]
                else:
                    # Normal find key value and put in payload
                    if field_name in host_data["host"]["fields"]:
                        #if field name starts with script_result, it may be JSON data we can parse before sending over
                        if "script_result" in field_name:
                            try:
                                #logging.debug("Trying parse script_result value as JSON: {},{}".format(field_name, alias_name))
                                elastic_payload["fields"][alias_name] = {
                                    "timestamp": host_data["host"]["fields"][field_name]["timestamp"],
                                    "value": json.loads(host_data["host"]["fields"][field_name]["value"])
                                }
                                logging.debug("Parsed script_result value as JSON: {},{}".format(field_name, alias_name))
                            except Exception as e:
                                elastic_payload["fields"][alias_name] = host_data["host"]["fields"][field_name]
                                logging.debug("Unable to parse script_result value as JSON: {},{}".format(field_name, alias_name))
                        else:
                            elastic_payload["fields"][alias_name] = host_data["host"]["fields"][field_name]

        # Prepare API request to elastic
        logging.debug(json.dumps(elastic_payload))
        credentials = ('%s:%s' % (elastic_username, elastic_password))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))

        elastic_headers = {
            "Content-Type": "application/json",
            'Authorization': '%s %s' % ("ApiKey" if elastic_apikey else "Basic", encoded_credentials.decode("ascii"))
        }
        elastic_request = urllib.request.Request(elastic_url + "/" + elastic_index + "/_doc/", headers=elastic_headers, data=bytes(json.dumps(elastic_payload), encoding="utf-8"))

        # Make API request to elasticsearch API to put document
        elastic_resp = urllib.request.urlopen(elastic_request, context=ssl_context) # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
        elastic_resp_parse = json.loads(elastic_resp.read().decode('utf-8'))
        logging.debug(elastic_resp_parse)
        
        # Check response from elasticsearch
        if "result" in elastic_resp_parse and (elastic_resp_parse["result"] == "created" or elastic_resp_parse["result"] == "updated"):
            logging.info("Sent host data to Elasticsearch succesfully!")
            response["succeeded"] = True
            response["result_msg"] = "Successfully sent data!"
            response["cookie"] = elastic_resp_parse["_id"]
        else:
            logging.error("Failed to send host data to Elasticsearch!")
            logging.debug(elastic_resp.read().decode('utf-8'))
            response["succeeded"] = False
            response["result_msg"] = "Failed API request to elasticsearch!"
    else:
        logging.error("Failed API Request to Forescout to get host data!")
        response["succeeded"] = False
        response["result_msg"] = "Failed API request to Forescout Web API server!"
except Exception as e:
    logging.error("Exception: {}".format(e))
    response["succeeded"] = False
    response["result_msg"] = "Exception! Something went wrong! Couldn't talk to Forescout, action parsing failed, or message to Elastic failed. See the debug logs for more info."