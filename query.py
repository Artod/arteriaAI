import json

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='query.log', level=logging.INFO)

from pinecone import Pinecone
api_key = "..."
index_name = 'arteria'
pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

import boto3
sagemaker = boto3.client('runtime.sagemaker')
sagemaker_endpoint_name = 'Endpoint-20240327-215135'

# get embedding from Sagemaker
def get_embedding(encoded_json, content_type):
    response = sagemaker.invoke_endpoint(EndpointName=sagemaker_endpoint_name, InferenceComponentName='huggingface-sentencesimilarity-all-MiniLM-L6-v2-20240328-173014', ContentType=content_type, Body=encoded_json)
    return json.loads(response['Body'].read())

def lambda_handler(event, context):
    query_params = event.get('queryStringParameters', {})
    text = query_params.get('text', None)
    if text is None:
        return {
            'statusCode': 400,
            'body': json.dumps("No 'text' query parameter provided.")
        }
        
    payload = [text]
    response = get_embedding(json.dumps(payload).encode('utf-8'), 'application/x-text')

    vector = response["embedding"][0]
    top_k = index.query(vector=[vector], top_k=5, include_metadata=True)
    
    results = []
    for match in top_k["matches"]:
        item = {
            "id": match["id"],
            "score": match["score"],
            "metadata": match["metadata"]
        }
        results.append(item)

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }