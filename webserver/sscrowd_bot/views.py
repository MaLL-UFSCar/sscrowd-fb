# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import pymongo

from django.shortcuts import render
from pprint import pprint
from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from tools import handle_message

class SSCrowdBotView(generic.View):

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == 'my_sscrowd_tk':
            return HttpResponse(self.request.GET['hub.challenge'])
        else: 
            return HttpResponse("Invalid Token")

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
    
    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):

        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))

        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:

                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:

                    #receive the message and acts accordingly
                    handle_message(message)

        return HttpResponse()
