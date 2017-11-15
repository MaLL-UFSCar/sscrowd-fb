import json
import requests
from django.conf import settings
from pprint import pprint
from sys import argv


def post_simple_message(fbid, message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?' \
                       'access_token={}'.format(settings.ACCESS_TOKEN)
    response_msg = json.dumps({"recipient": {"id": fbid},
                               "message": {"text": message}})
    status = requests.post(post_message_url,
                           headers={"Content-Type": "application/json"},
                           data=response_msg)
    pprint(status.json())

def post_quick_reply(fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?' \
                       'access_token={}'.format(settings.ACCESS_TOKEN)

    response_msg = json.dumps({"recipient": {"id": fbid},
                               "message": {"text": "here is the quicj reply",
                                           "quick_replies": [
                                             {
                                              "content_type":"text",
                                              "title":"One",
                                              "payload":"pick 1"
                                             },
                                             {
                                              "content_type":"text",
                                              "title":"Two",
                                              "payload":"pick 2"
                                             }
                                           ]
                               }
                              })

    status = requests.post(post_message_url,
                           headers={"Content-Type": "application/json"},
                           data=response_msg)


    pprint(status.json())
