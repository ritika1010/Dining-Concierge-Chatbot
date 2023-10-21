#GETS USER MSG
#SENDS TO LEX INTENT AND PROCESSES
#RESPONDS TO USER

import json
import boto3

client = boto3.client('lexv2-runtime')
sqs_client = boto3.client('sqs')

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
