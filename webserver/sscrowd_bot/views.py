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

from .utils import post_simple_message
from .utils import post_quick_reply

from datetime import datetime, timedelta
from pymongo import MongoClient

import os


class SSCrowdBotView(generic.View):

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == 'my_sscrowd_tk':
            return HttpResponse(self.request.GET['hub.challenge'])
        else: 
            return HttpResponse("Invalid Token")

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
    
    def save_userid(self,userid):
        f = open('userids', 'w')
        f.write(userid)
        f.close()

    def create_user(self,fbid):
        conn = MongoClient('mongodb://localhost:27017')

        db_fbusers = conn['fbusers']
        
        today = datetime.today()

        #the next interaction for a new user is 1 minute after its creation
        next_interaction = today + timedelta(minutes=1)

        #sets fbid to be unique
        db_fbusers.users.create_index([('fbid',pymongo.ASCENDING)], unique=True)

        #try to insert the new user
        try:
            db_fbusers.users.insert_one(
                {
                    'fbid':fbid, 
                    'next_interaction':next_interaction.strftime("%Y%m%d%H%M%S")
                },
            )
        except pymongo.errors.DuplicateKeyError:
            pass

    def send_poll(question,options):
        post_simple_message(fbid,message)
        post_quick_reply(fbid,"Your reply:",options)

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

                    #save the fbid if this is first contact with user
                    self.create_user(message['sender']['id'])
                    pprint(message)  
   
        return HttpResponse()

