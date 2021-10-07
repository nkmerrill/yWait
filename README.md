# yWait
## About
yWait is a web app that allows users to compare busyness of multiple locations to determine the best times to go to different businesses.

## How it Works
Built on the Django framework, this App uses the https://besttime.app REST api to pull foot traffic of entered locations and presents that data in both a table and a chart. That data can then be compared with other locations in a comparison set.

## How to Use
As this App uses a commercial API to function, users will need to run their own copy with their own API key. By default, this key is looked for in the environment variable "APIKEY" though this can be modified in the [yWait/models.py](yWait/models.py) file on line 53. Alternatively, modifying the "TEST" variable can allow the app to use a JSON file as input instead. A location can be set in the "TESTRESPONSE" variable, and a default [sampleresponse.json](yWait/sampleresponse.json) file is provided with the correct api response format.

Additionally, the App was designed on Replit and may not work outside of a Replit environment.

## Disclosure
This app is provided publically as-is and will not be maintained. It is provided only for demonstration purposes, and was completed as a school project by [@nkmerrill](https://github.com/nkmerrill) and should not be used in any production capacity.  
