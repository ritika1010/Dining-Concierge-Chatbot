#GETS USER MSG
#SENDS TO LEX INTENT AND PROCESSES
#STORES IN SQS
#RESPONDS TO USER

import json
import boto3

client = boto3.client('lexv2-runtime')
sqs_client = boto3.client('sqs')

def send_to_sqs(message_body):
    queue_url = 'https://sqs.us-east-1.amazonaws.com/252549629269/MyUserPrefQueue'
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body)
    )
    print(f"Message sent to SQS: {response['MessageId']}", message_body)
    
def send_msg_toLex(msg_from_user):
  # Initiate conversation with Lex
  response = client.recognize_text(
    botId='SM0NIZJZID', # MODIFY HERE
    botAliasId='TSTALIASID', # MODIFY HERE
    localeId='en_US',
    sessionId='testuser',
    text=msg_from_user)
  
  msg_from_lex = response.get('messages', [])
  if msg_from_lex:
    print(f"Message from Chatbot: {msg_from_lex[0]['content']}")
    print(response)
  
  slots = response.get('sessionState', {}).get('intent', {}).get('slots', {})
  print("SLOTS =====", slots)
  if msg_from_lex:
    print(f"Message from Chatbot: {msg_from_lex[0]['content']}")
    
    if slots:    
      
      # Send slots data to SQS
      if slots['cuisine'] is not None and slots['location'] is not None and slots['email'] is not None and slots['DiningTime'] is not None and slots['peoplenumber'] is not None:
        updated_slots = {
          'cuisine': slots['cuisine']['value']['interpretedValue'],
          'location': slots['location']['value']['interpretedValue'],
          'email': slots['email']['value']['interpretedValue'],
          'peoplenumber': slots['peoplenumber']['value']['interpretedValue'],
          'DiningTime': slots['DiningTime']['value']['interpretedValue']
        }
        send_to_sqs(updated_slots)
    
  return msg_from_lex
  

def lambda_handler(event, context):
  #MSG FROM USER
  msg_from_user = event['messages'][0]['unstructured']['text']
  print(f"Message from frontend: {msg_from_user}")
  
  #VALIDATE USER MSG
  # validate_msg(msg_from_user)
  
  #SEND VALIDATED MSG TO LEX
  msg_from_lex = send_msg_toLex(msg_from_user)
 
  resp = {
  "messages": [
    {
      "type": "unstructured",
      "unstructured": {
        "id": "string",
        "text": msg_from_lex[0]['content'],
        "timestamp": "string"
      }
    }
    ]
  }
  return resp
