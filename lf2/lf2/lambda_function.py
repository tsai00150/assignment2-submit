import json
import boto3 
from opensearch import opensearch
import urllib

BUCKET_URL = "https://s3.us-east-1.amazonaws.com"
# test codepipeline
# def build_search_response(stype, prop) -> dict:
#     return 
#     {
#   "type" : "object",
#   "properties" : {
#     "results" : {
#       "type" : "array",
#       "items" : {
#         "$ref":"https://apigateway.amazonaws.com/restapis/l0k98lmm4l/models/Photo"
#       }
#     }
#   }
# }

def build_photo_object(object_key:str, bucket:str, labels:str) -> dict:
    photo = {
        "url" : f"{BUCKET_URL}/{bucket}/{object_key}",
        "labels" : labels
    }
    
    return photo

def get_images(response:dict):
    print(type(response))
    body = response["body"]
    hits = body["hits"]["hits"]
    
    results = []
    for hit in hits:
        source = hit["_source"]
        
        object_key = source.get("objectKey")
        bucket = source.get("bucket")
        labels = source.get("labels")
        
        photo = build_photo_object(object_key, bucket, labels)
        results.append(photo)
        
    return {
        "results" : results
    }
        
def get_tokens(event:dict) -> str:
    t = event["q"]
    t = t.strip().lower()
    
    return t.split(" ")

def query_lex_bot(tokens:str):
    """
    Send query to lambda bot and disambiguate the labels
    """
    if len(tokens) <= 1:
        return None
        
    query = " ".join(tokens)
    
    client = boto3.client("lexv2-runtime")
   
    # Get keywords from lex
    for i in range(2):
        response = client.recognize_text(
                botId='MVYMRHXINK', # MODIFY HERE
                botAliasId='MPAJE5DNLR', # MODIFY HERE 
                localeId='en_US',
                sessionId='testuser',
                text=query
        )
    
    interpretations = response.get("interpretations")[0]
    intent = interpretations.get("intent")
    slots = intent.get("slots")
    keywords = slots.get("keywords")
    
    if not keywords:
        return None
        
    values = keywords.get("values")
    
    labels = []
    for v in values:
        label = v["value"]["interpretedValue"]
        labels.append(label)
    
    return labels

def lambda_handler(event, context):
    # TODO implement
    
    print(event)
    
    tokens = get_tokens(event)
    print("Tokens:", tokens)
    labels = query_lex_bot(tokens)
    
    print("Labels")
    print(labels)
    
    # Search the photos OpenSearch index for results
    if labels is None:
        response = opensearch.query(tokens)
    else:
        response = opensearch.query(labels)
        
        
    results = get_images(response)
    print("Results")
    print(results)
    
    return results
