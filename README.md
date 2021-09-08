
# connect_elasticsearch

Forescout EyeExtend Connect app for Elastic

## Allow unsigned app install on Forescout

When you import an app, the signature of the app is validated to see if it has a valid Forescout signature. If the validation succeeds, the app is imported. If the validation fails, an error message is displayed and the app is not imported. To allow an app with an invalid signature to be imported use the following command on the Enterprise Manager:

`fstool allow_unsigned_connect_app_install true`

This is a global command. It disables the enforcement of signature validation for all apps that are imported after the command is run, including apps with invalid or missing signatures.

## Creating zip

You have to make sure to not include any "extra" files when zipping up the app for import into Forescout. If you use the default "Compress" item in Finder on macOS, an `__macosx` folder is included which will cause Forescout to balk. Avoid this by opening terminal and going into the `app` directory and running the zip command manually:

`rm -f import_app.zip; zip import_app.zip ./*`

Note the above command also deletes the `import_app.zip` file if it's there so you have a fresh copy.

## About

This Elasticsearch app for Forescout EyeExtend Connect allows you to send data from Forescout into an Elasticsearch index.

- The app makes an API request directly to Elasticsearch and uses either elastic BASIC auth or an API key to authenticate.

- The app leverages the Forescout EyeExtend Connect Web Service API in order to obtain the data about a host and then send to elasticsearch, consequently, data is send to elasticsearch in nearly the same format as if you were consuming it via the Forescout OIM Web API `/host/ip/<host_ip>` API

- There is support for selecting custom host fields as well as renaming fields

## Setup

1) Go to Web API in Options and create a username/password for this App to use and make sure the API is allowed to be accessed from all Forescout appliance IP addresses
 - *This app uses the Forescout Web API to gather information about endpoints and process it to create other attributes on endpoints.*
 - Create a complex username/password combonation as this username/password can be used to pull all information about hosts and we don't want this being leaked/guessed
 - We'll need this username/password during the app import
 - Note the token expiration time in the Web API settings. We'll need to use this during the App setup as the app needs to know how long tokens are valid for so it can refresh it before it expires

2) Go to Connect in Options > Import this app

3) The System Description dialog will appear, click Add

4) Enter the information for the Elasticsearch connection
 - URL: <http(s)://elasticsearch_server:port>
 - Index Name: Name of the default index to send data to if not specified in an action
 - Username/API Key ID: Username or API Key ID for elastic authentication
 - Password/API Key: Password or API Key for elastic authentication
 - Username/Password is API Key?: Check if you provided API Key based credentials and not BASIC credentials

5) Enter the information for the Forescout Web API connection
 - URL: <https://<IP>  address  of  appliance  running  Web  API  (EM)>
 - Username: username from step 1
 - Password: password from step 1

6) Go through the rest of the settings and set as desired.
 - Note that on the "API Settings" pane:
  - The "Number of API queries per second" number can be adjusted -- this throttle setting will limit the amount of requests to the Web API for host data. You can adjust this setting to be larger to allow for faster resolution of the related properties, just be careful as at some point the Web API will become overloaded and you'll start getting errors. Be careful here.
  - Make sure to set the "Forescout Web API Authorization Interval" to a value less than the Web API token expiration time from step 1.

7) Complete the app setup and Apply the Connect settings to start the app.

## Actions

### Send Host Data

Found under the `Audit` menu, this action allows you to send host data to Elasticsearch. When you select the action, you can select to either send `All Data` or make a selection of fields via a free-form text box (`Forescout host field list`).

  

If the `All Data` checkmark is selected (value == `true`), all data will be sent to Forescout, regardless of what is typed into the `Forescout host field list` textbox.

  

The `Forescout host field list` field takes a comma seperated list of host properties to send to elasticsearch from the Forescout `/host/<host_id>` API response. It supprots feild renaming via a parenthesis after the field name. The field renaming specification is required (it can be the same name as the field attribute). The `configuration_utility` app can help you generate this comma seperated list. Additionally, a single wildcard character, `*`, can be included in a field specification to include fields matchinga certain pattern. The `*` character must be included in the field rename specificiation -- the wildcard matched characters are replaced in the field rename specification.

  

An example specification follow:

  

`in-group(device_groups),scap::*::oval_check_result(scap::*::oval_check_result),hostname(hostname),nbthost(nbthost),segment_path(segment_path),online(online),nbtdomain(nbtdomain),dhcp_hostname(dhcp_hostname),user(user),va_netfunc(va_netfunc)`

  

Above we've renamed the `in-group` property, included a wildcarded inclusion of SCAP scan results, and some additional host properties. In the example above, the string that is matched via the `*` in the host data is used to replaced the `*` in the rename field naming.

  

Supports Undo: Yes, via calling the DELETE method on the document that was POSTed to Elasticsearch. This will cause the host to be DELETEed from the index by the Forescout ID of the Host