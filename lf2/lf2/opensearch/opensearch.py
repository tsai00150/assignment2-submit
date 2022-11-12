import boto3
import json
import requests
from requests_aws4auth import AWS4Auth
import json

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
host = 'https://search-opensearch-zsfvslqm09a9-4lecmit6k64rsp4z2wlze7pq7u.us-east-1.es.amazonaws.com'
index = 'photos'
url = host + '/' + index + '/_search'

headers = { "Content-Type": "application/json" }

def query(labels):
    
    query = {
        "size": 25,
        "query": {
            "match": {
                "labels": {
                    "query"     : ', '.join(labels),
                    "operator"  : "or",
                    "fuzziness" : "AUTO"
                }
            }
        }
    }
    print(query)
    
    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
    print(r.content)
    response = {
        "body" : json.loads(r.text)
    }
    
    return response

if __name__ == "__main__":
    response = query('cat')
    print(response)
