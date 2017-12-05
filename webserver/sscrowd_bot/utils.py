#TBD

import json
import requests
import argparse
from sscrowdconfig import ConfigSSCrowdFB
#from django.conf import settings
from pprint import pprint
from sys import argv

ssc_config = ConfigSSCrowdFB()

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

    if status.status_code == 200:
        return (True,response_msg)
    else:
        return (False,response_msg)

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

    print(status.json())

    if status.status_code == 200:
        return (True,response_msg)
    else:
        return (False,response_msg)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--sm")
    parser.add_argument("--qr")
    parser.add_argument("--fbid")
    parser.add_argument("-q","--questionid")
    parser.add_argument("-m","--message")
 
    args = parser.parse_args()

    if args.sm:
        post_simple_message(args.fbid,args.message)
    
    if args.qr:
        post_quick_reply(args.fbid,args.message,args.questionid)
