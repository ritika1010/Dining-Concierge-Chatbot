#GETS DATA FROM SLOTS IN DINING INTENT
#VALIDATES IT
#PUSHES IN SQS

import math
import datetime

import boto3
import json
import time
import os
import logging
import re

# maybe import math and re, To-do later

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---

def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']


def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']
    return {}


def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        logger.debug('resolvedValue={}'.format(slots[slotName]['value']['resolvedValues']))
        return slots[slotName]['value']['interpretedValue']
    else:
        return None


def elicit_slot(intent_request, session_attributes, slot, slots, message):
    print("in elicitng slot")
    return {'sessionState': {'dialogAction': {'type': 'ElicitSlot',
                                              'slotToElicit': slot,
                                              },
                             'intent': {'name': intent_request['sessionState']['intent']['name'],
                                        'slots': slots,
                                        'state': 'InProgress'
                                        },
                             'sessionAttributes': session_attributes,
                             #  'originatingRequestId': '70d49ca7-53de-4e1e-ac0a-70ecfc45b70a'
                             },
            'sessionId': intent_request['sessionId'],
            'messages': [message],
            'requestAttributes': intent_request['requestAttributes']
            if 'requestAttributes' in intent_request else None
            }


def build_validation_result(isvalid, violated_slot, slot_elicitation_style, message_content):
    return {'isValid': isvalid,
            'violatedSlot': violated_slot,
            'slotElicitationStyle': slot_elicitation_style,
            'message': {'contentType': 'PlainText',
                        'content': message_content}
            }


def GetItemInDatabase(postal_code):
    """
    Perform database check for transcribed postal code. This is a no-op
    check that shows that postal_code can't be found in the database.
    """
    return None


def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent'],
            'originatingRequestId': '2d3558dc-780b-422f-b9ec-7f6a1bd63f2e'
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def delegate(intent_request, slots):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Delegate"
            },
            "intent": {
                "name": intent_request['sessionState']['intent']['name'],
                "slots": slots,
                "state": "ReadyForFulfillment"
            },
            'sessionId': intent_request['sessionId'],
            "requestAttributes": intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
        }}

def current_time():
    now = datetime.datetime.now()
    hour = str(now.hour).zfill(2)
    minute = str(now.minute).zfill(2)
    return f"{hour}:{minute}"

def validationProcess(Location, Cuisine, Numberofpeople, Email):
    # Location Validation
    print("in validation")
    print(Location)
    if Location:
        print('1234Locatioon')
        if Location.lower() not in ['new york city', 'manhattan', 'bronx', 'queens', 'nyc', 'new york']:
            print('5667errorcomingup')
            return build_validation_result(False,
                                           'location',
                                           'SpellbyWord',
                                           'Currently this is not an available location. Please enter location, like Manhattan')

    # Cuisine Validation:
    if Cuisine:
        if Cuisine.lower() not in ['chinese', 'ethiopian', 'thai', 'american', 'french', 'italian', 'indian',
                                   'japanese', 'spanish']:
            return build_validation_result(False, 'cuisine', 'SpellbyWord',
                                           'Sorry! The one you just entered is invalid! '
                                           'Please choose from the following options: '
                                           'chinese, japanese, thai, american, french, italian, indian')

    # Numberofpeople Validation

    if Numberofpeople:
        if int(Numberofpeople) not in range(1, 11):
            return build_validation_result(False,
                                           'peoplenumber',
                                           'SpellbyWord',
                                           'Number of people should be between 1 and 10')

    # Date Validation
    
    print('returningTrue!!!!!')
    return build_validation_result(True,
                                   '',
                                   'SpellbyWord',
                                   '')


def DiningSuggestionsIntent(intent_request):
    state = intent_request['sessionState']

    Location = get_slot(intent_request, "location")
    Cuisine = get_slot(intent_request, "cuisine")
    Numberofpeople = get_slot(intent_request, "peoplenumber")
    Email = get_slot(intent_request, "email")

    session_attributes = get_session_attributes(intent_request)

    # type of event that triggered the function
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        print("Here we are in DialogCodeHook!")

        slots = get_slots(intent_request)

        resOfValidation = validationProcess(Location, Cuisine, Numberofpeople, Email)
        print("result of validation")
        print(resOfValidation)
        if not resOfValidation['isValid']:
            slots[resOfValidation['violatedSlot']] = None
            print("now eliciting")
            print(resOfValidation)
            result = elicit_slot(intent_request, session_attributes, resOfValidation['violatedSlot'], slots,
                                 resOfValidation['message'])
            print("the result of elicit slot")
            print(result)
            return result

    if not Location or not Numberofpeople or not Email or not Cuisine:
        return delegate(intent_request, get_slots(intent_request))
    else:
        updated_slots = get_slots(intent_request)
        send_to_sqs(updated_slots)
        return close(intent_request,
                     session_attributes,
                     'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'Thanks. We will send you email shortly'})


# --- Intents ---

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    intent_name = intent_request['sessionState']['intent']['name']
    # state = intent_request['sessionState']

    if intent_name == 'DiningSuggestionsIntent':
        result = DiningSuggestionsIntent(intent_request)
        print("the final dining suggestion intent")
        print(result)
        return result
    print("Error!", intent_name)


# --- Main handler ---

def lambda_handler(event, context):
    """
    Route the incoming request based on the intent.
    The JSON body of the request is provided in the event slot.
    """

    # By default, treat the user request as coming from
    # Eastern Standard Time.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    logger.debug('event={}'.format(json.dumps(event)))
    response = dispatch(event)
    print("The final response of the lambda handler")
    print(response)
    return response

def send_to_sqs(message_body):
    queue_url = 'https://sqs.us-east-1.amazonaws.com/252549629269/MyUserPrefQueue'
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body)
    )
    print(f"Message sent to SQS: {response['MessageId']}", message_body)
    