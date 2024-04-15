import base64
import os
import boto3
import json
import requests
from requests.auth import HTTPBasicAuth 

region = 'ap-southeast-1'
service = 'es'

index = 'mysql_data'
type = '_doc'

headers = { "Content-Type": "application/json" }


def lambda_handler(event, context):
    host = os.getenv("ES_DOMAIN")  # the OpenSearch Service domain, including https://
    url = host + '/' + index + '/' + type + '/'
    
    print("START...")
    count = 0
    for record in event['Records']:
        print(record)
        #id = record['eventID']
        timestamp = record['kinesis']['approximateArrivalTimestamp']
        # Kinesis data is base64-encoded, so decode here
        message = base64.b64decode(record['kinesis']['data'])
        message_json = json.loads(message)
        print("message",message_json)
        op_type = message_json['type']
        if op_type == ('WriteRowsEvent'):
            id = str(message_json['row']['values']['UNKNOWN_COL0'])
        else:
            id = str(message_json['row']['after_values']['UNKNOWN_COL0'])
            
        # Create the JSON document
        document = { "id": id, "timestamp": timestamp, "message": message }

        # Index the document
        r = requests.put(url + id, auth=HTTPBasicAuth(os.getenv("ES_USER"), os.getenv("ES_PASSWORD")), json=document, headers=headers)
        count += 1
        print("document: ", document)
        print("requests: ", r)
        print("URL: ", url + id)
        print("END")
    return 'Processed ' + str(count) + ' items.'