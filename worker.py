import json
import os

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='worker.log', level=logging.INFO)

from pypdf import PdfReader

import boto3
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
sagemaker = boto3.client('runtime.sagemaker')
sagemaker_endpoint_name = 'Endpoint-20240327-215135'

# Get embedding from Sagemaker
def get_embedding(encoded_json, content_type):
    response = sagemaker.invoke_endpoint(EndpointName=sagemaker_endpoint_name, InferenceComponentName='huggingface-sentencesimilarity-all-MiniLM-L6-v2-20240328-173014', ContentType=content_type, Body=encoded_json)
    return json.loads(response['Body'].read())

from pinecone import Pinecone
api_key = "..."
index_name = 'arteria'
pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Upsert a vector with specified ID and metadata
def upsert_vector(object_key, vectors, chunks):
    payload = list()
    for i, [vector, chunk] in enumerate(zip(vectors, chunks)):
        # TODO: sanitize object_key
        # TODO: add user id as prefix
        unique_id = f"user1#{object_key}#chunk{i}"
        metadata = {"text": chunk}
        payload.append((unique_id, vector, metadata))

    index.upsert(vectors=payload)

def lambda_handler(event, context):
    # TODO: error handling with logger
    
    # STEP 1: Parse the S3 event
    # TODO: add batch processing of messages from SQS
    record = event['Records'][0]
    s3_event = json.loads(record['body'])
    s3_record = s3_event['Records'][0]

    bucket_name = s3_record['s3']['bucket']['name']
    object_key = unquote_plus(s3_record['s3']['object']['key'])
    
    download_path = f'/tmp/{object_key}'
    
    # TODO: for idempotency add metadata to the file in S3 with current stage (PROCESSING, PROCESSED etc)
    s3.download_file(bucket_name, object_key, download_path)
    
    
    # STEP 2: Process pdf
    # TODO: Check for correct format etc
    reader = PdfReader(download_path)
    pages = [page.extract_text() for page in reader.pages]

    try:
        os.remove(download_path)
    except OSError as e:
        logger.error(f"Error deleting {download_path}: {e.strerror}")
        
        
    # STEP 3: Get embedding for every chunk
    # TODO: Sagemaker endpoint has limit 6mb for payload
    payload = pages
    response = get_embedding(json.dumps(payload).encode('utf-8'), 'application/x-text')
    vectors = response["embedding"]


    # STEP 4: Save to Pinecone
    # TODO: Pinecone has limit 40kb for metadata
    upsert_vector(object_key, vectors, pages)
    
    return {
        'statusCode': 200,
        'body': json.dumps(event, indent=2)
    }