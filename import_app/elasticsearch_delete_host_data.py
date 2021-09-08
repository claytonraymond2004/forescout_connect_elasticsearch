import json
import urllib.request

# Hold response to Forescout EyeExtend Connect
# Like the action response, the response object must have a "succeeded" field to denote success. It can also optionally have
# a "result_msg" field to display a custom test result message.
response = {}

# Get Elasticsearch API Details (To delete data from)
elastic_url = params["connect_elasticsearch_url"]
elastic_index = params["connect_elasticsearch_index"]
elastic_username = params["connect_elasticsearch_username"]
elastic_password = params["connect_elasticsearch_password"]
elastic_doc_id = params["cookie"]


try:
    # Prepare API request to elastic
    credentials = ('%s:%s' % (elastic_username, elastic_password))
    encoded_credentials = base64.b64encode(credentials.encode('ascii'))
    elastic_headers = {
        "Content-Type": "application/json",
        'Authorization': 'Basic %s' % encoded_credentials.decode("ascii")
    }
    elastic_request = urllib.request.Request(elastic_url + "/" + elastic_index + "/_doc/" + elastic_doc_id, headers=elastic_headers, method='DELETE')

    # Make API request to elasticsearch API to put document
    elastic_resp = urllib.request.urlopen(elastic_request, context=ssl_context) # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
    elastic_resp_parse = json.loads(elastic_resp.read().decode('utf-8'))
    logging.debug(elastic_resp_parse)
    
    # Check response from elasticsearch
    if "result" in elastic_resp_parse:
        logging.error("Failed to delete host data in Elasticsearch!")
        response["succeeded"] = False
        response["result_msg"] = "Failed API request to elasticsearch!"
    else:
        logging.info("Deleted host data to Elasticsearch!")
        response["succeeded"] = True
        response["result_msg"] = "Made delete API request to elasticsearch!"
except Exception as e:
    logging.error(e)
    response["succeeded"] = False
    response["result_msg"] = "Exception! Something went wrong! See the debug logs for more info."