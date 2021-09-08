import urllib
import urllib.request
import json

# Hold response to Forescout
response = {}

instance = params["connect_elasticsearch_url"]
username = params["connect_elasticsearch_username"]
password = params["connect_elasticsearch_password"]

# create a password manager
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
# Add the username and password.
password_mgr.add_password(None, instance, username, password)
handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
# create "opener" (OpenerDirector instance)
opener = urllib.request.build_opener(handler)

# make requst to elasticsearch base URL
request = opener.open(instance)
elastic_response = json.loads(request.read())

if "name" not in elastic_response:
   response["succeeded"] = False
   response["result_msg"] = str(elastic_response)
else:
    response["succeeded"] = True
    response["result_msg"] = "Successfully connected to Elasticsearch: \n" + json.dumps(elastic_response, indent=2)