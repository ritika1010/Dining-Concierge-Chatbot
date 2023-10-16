#INSERTS DATA TO DYNAMODB
import json
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    
    file_path = "data.json"
    
    db = boto3.resource('dynamodb')
    table = db.Table('YelpRestaurantData')
    
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            line_json = json.loads(line)
            response = table.put_item(Item=line_json)
 