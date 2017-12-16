#TBD

import json
import requests
import argparse
import logging
from sscrowdconfig import ConfigSSCrowdFB
#from django.conf import settings
from pprint import pprint
from sys import argv

ssc_config = ConfigSSCrowdFB()

logger = logging.getLogger(__name__)

ACCESS_TOKEN = ssc_config.access_token

def post_simple_message(fbid, message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?' \
                       'access_token={}'.format(ACCESS_TOKEN)
    response_msg = json.dumps({"recipient": {"id": fbid},
                               "message": {"text": message}})
    status = requests.post(post_message_url,
                           headers={"Content-Type": "application/json"},
                           data=response_msg)
    pprint(status.json())

    return check_status(status.status_code)

def post_quick_reply(fbid,text,option_list,payload,identifier):

    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?' \
                       'access_token={}'.format(ACCESS_TOKEN)

    reply_list = []

    #build the option list according to the list in the configuration file
    for option in option_list:
        reply_list.append({"content_type":"text","title":option,"payload":payload}) 

    response_msg = json.dumps({"recipient": {"id": fbid},
                               "message": {"text": text,"quick_replies":reply_list},
                               "identifier":identifier
                              })

    status = requests.post(post_message_url,
                           headers={"Content-Type": "application/json"},
                           data=response_msg)

    pprint(status.json())

    return check_status(status.status_code)

def post_greeting():

    post_message_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?' \
                       'access_token={}'.format(ACCESS_TOKEN)

    response_msg = json.dumps({"greeting":[{
                                            "locale":"default",
                                            "text":"my greeting"
                                           }]
                              })

    status = requests.post(post_message_url,
                           headers={"Content-Type": "application/json"},
                           data=response_msg) 
    pprint(status.json())

    return check_status(status.status_code)

def check_status(code,response_msg):

    status = False

    log_message = "facebook message API returned code "+code+" for request "+response_msg
    if code == 200:
        status = True
        logger.info(log_message)
    else:
        logger.error(log_message)

    return (status,response_msg)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--sm")
    parser.add_argument("--qr")
    parser.add_argument("--gr")
    parser.add_argument("--fbid")
    parser.add_argument("-q","--questionid")
    parser.add_argument("-m","--message")
 
    args = parser.parse_args()

    if args.sm:
        post_simple_message(args.fbid,args.message)
    
    if args.qr:
        post_quick_reply(args.fbid,args.message,args.questionid)

    if args.gr:
       post_greeting()
