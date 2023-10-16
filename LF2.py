#GETS USER PREFERENCES FROM SQS 
#SEARCHES DATA FROM OPENSEARCH
#SEARCHES DATA FROM DYNAMODB
#SENDS EMAIL USING SNS

import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr


import os

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


REGION = 'us-east-1'
HOST = 'search-restaurants-ehpatsisdvnn2cagv2hxxfwui4.us-east-1.es.amazonaws.com'
INDEX = 'restaurants'

sqs_client = boto3.client('sqs')
sns = boto3.client('sns')
ses = boto3.client('ses')


def get_sqs():
    print("inside get sqs")
    queue_url = 'https://sqs.us-east-1.amazonaws.com/252549629269/MyUserPrefQueue'
    response = sqs_client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[
                'All'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0 # Adjust the batch size as needed
    )
    # print("SQS MSG", response)
    return response
    
def send_email_SNS(phone_number, msg):
    print("inside get send sms")


    # Specify the sender's email address verified in SES
    topic_arn = "arn:aws:sns:us-east-1:252549629269:Dining_Suggestion_Details"

    # Publish the message to the topic
    # response = sns.publish(
    #     TopicArn=topic_arn,
    #     Message=msg,
    #     Subject='Hi Dining Suggestions',  # Specify a subject for the email
    # )
    response = sns.publish(
        TopicArn=topic_arn,
        Message=msg,
        Subject='Hi Dining Suggestions',
        MessageAttributes={
            'email': {
                'DataType': 'String',
                'StringValue': 'agamyatani@gmail.com'
            }
        }
    )
    print("SNS EMAIL" , response)

    
    
    
def lambda_handler(event, context):
    
    print("#GET USER PREFERENCE LATEST")
    sqs_res = get_sqs()
    print("SQS - content==== ",sqs_res['Messages'][0]['Body'].replace('\\"', '"'))
    sqs_data = json.loads(sqs_res['Messages'][0]['Body'].replace('\\"', '"'))
    db = boto3.resource('dynamodb')
    table = db.Table('YelpRestaurantData')
    
    print("#SEARCH OPENSEARCH ON CUISINE TYPE FROM PREFERENCE")
    results = query(sqs_data["cuisine"])
    # print('Results from opensearch : ' ,results)
    
    #REPLY MSG TO USER TEMPLATE
    msg = "Hello! Here are my " + sqs_data["cuisine"] +" restaurant suggestions for " + sqs_data["peoplenumber"] + " people, for today at " + sqs_data["DiningTime"] + " : "
    
    print('#SEARCH RESTAURANT DETAILS FOR ALL RESULTS FROM OPENSEARCH')
    for r in results:
        data = lookup_data({'business_id': r['business_id']}) # 2
        submsg = data['name'] + " located at " + data['address'] + ", "
        msg = msg + submsg
        
    msg = msg.replace('None' , '')
    # print(msg)
    
    print('#SEND SMS')
    phone_number = '+16463694576'
    send_email_SNS(phone_number, msg)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
        }
        ,
        'response of restaurants ' :{
          "name": msg
        }
        
        
        
        
    }
    


    
def lookup_data(key, db=None, tableN='YelpRestaurantData'):
    if not db:
        db = boto3.resource('dynamodb')
    # creates a reference to the table
    table = db.Table(tableN)
    try:
        response = table.get_item(Key=key)
        # response = table.get_item(Key=key)
        # print("Restaurants available",response)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        return response['Item']
        
        
#OPENSEARCH      
def query(term):
    # q = {'size': 5, 'query': {'multi_match': {'query': term}}}

    q = { 'size': 5,
        "query": {
            "bool": {
                "should": [
                    {"match": {"cuisine": term}},
                ]
            }
        }
    }
    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    res = client.search(index=INDEX, body=q)
    print("res -----" ,res)

    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])

    return results


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)