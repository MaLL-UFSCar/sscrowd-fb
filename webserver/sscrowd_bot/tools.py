#this file contains the SS-Crowd tools to interact with Facebook Messenger

import sys
import os
import argparse
import json
import pymongo
import pprint
import random
import logging

from datetime import datetime
from utils import post_quick_reply
from utils import post_simple_message
from utils import post_greeting
from sscrowdconfig import ConfigSSCrowdFB

from datetime import datetime,timedelta

from pymongo import MongoClient
from pymongo import database
from bson import ObjectId

#create a configuration object
ssc_config = ConfigSSCrowdFB()

#get database address
db_address = ssc_config.db_address

#connection to mongo database
conn = MongoClient(db_address)

db_fbuser = conn['fbuser']

logger = logging.getLogger(__name__)

def build_experiment(exp_name,question_file):

    db_exp = conn[exp_name]

    schedule(db_exp,question_file)

def schedule(db_exp,question_file):

    #sets questions to be unique
    db_exp.schedule.create_index([('question',pymongo.ASCENDING)], unique=True)

    with open(question_file,'r') as ql_raw:

        #for all questions in the question file
        for question in ql_raw:

            #will not allow duplicated questions
            try:
                db_exp.schedule.insert_one({"question":question})
            except pymongo.errors.DuplicateKeyError:
                logger.error("failed attempt to duplicate question "+question)
            

def create_user(fbid):

    #sets fbid to be unique
    db_fbuser.user.create_index([('fbid',pymongo.ASCENDING)], unique=True)

    #will not allow duplicated users 
    try:
        db_fbuser.user.insert_one(
	    {
	        'fbid':fbid,
	        'last_interaction':datetime.today(),
                'next_interaction':7,
	        'active':False
	    },
        )
    except pymongo.errors.DuplicateKeyError:
        logger.error("failed attempt to duplicate fbid "+fbid)

def unsubscribe(fbid):

    db_fbuser.user.update_one({"fbid":fbid},
                            {"$set":{"active":False}},
                            upsert=False
                           )

    post_simple_message(fbid,ssc_config.unsubscribe_answer)

def subscribe(fbid):

    db_fbuser.user.update_one({"fbid":fbid},
                            {"$set":{"active":True}},
                            upsert=False
                           )

    post_simple_message(fbid,ssc_config.subscribe_answer)

def handle_message(message):

    pprint.pprint(message)

    post_greeting()

    fbid = message['sender']['id']

    #try to create user
    create_user(fbid)

    message_obj = message['message']

    #if the message is an option of a SS-Crowd quick reply
    if message_obj.has_key('quick_reply'):

        payload = message['message']['quick_reply']['payload'].split('#')
        option = message['message']['text']

        action = payload[0]	#the action to be performed by this handler
        exp_name = payload[1]	#the name of the experiment
        
        if action == 'begin_question':		#the user agreed to answer questions
            if option == ssc_config.begin_options[0]:	#option == Yes
                #ask the first question
                ask_question(exp_name,fbid)

            elif option == ssc_config.begin_options[1]: #option == No
                #send message to user and leave program
                post_simple_message(fbid,ssc_config.no_begin_answer)

            elif option == ssc_config.begin_options[2]:	#option == Unsubscribe
                unsubscribe(fbid)

        elif action == 'get_answer':	#the user sent an answer

            schedule_id = payload[2]
             
            #save the answer
            record_answer(exp_name,schedule_id,message)

            #ask if user wants to keep answering
            post_quick_reply(fbid,
                             ssc_config.ask_one_more_text,
                             ssc_config.ask_one_more_options,
                             'ask_one_more#'+exp_name,
                             None
                            )

        elif action == 'ask_one_more':	#the user decides to keep answering
            if option == ssc_config.ask_one_more_options[0]:	#option == Yes
                #ask another question
                ask_question(exp_name,fbid)
            elif option == ssc_config.ask_one_more_options[1]:	#option == No
                #send message to user and leave program
                post_simple_message(fbid,ssc_config.no_more_answers)

        elif action == 'subscribe':
            if option == ssc_config.subscribe_options[0]:
                subscribe(fbid)
            elif option == ssc_config.subscribe_options[1]:
                post_simple_message(fbid,ssc_config.no_subscribe_answer)
            
    else:
        #send message to explain that the bot cannot answer at the moment
        post_simple_message(fbid,ssc_config.no_quick_reply_answer)

        user = db_fbuser.user.find_one({"fbid":fbid})

        #pick a random experiment
        exp_name = random.choice(ssc_config.active_experiments)

        if not user['active']:	#if user is not subscribed
            sts2,msg2 = post_quick_reply(fbid,
                                         ssc_config.subscribe_text,
                                         ssc_config.subscribe_options,
                                         'subscribe#'+exp_name,
                                         None
                                        )
        
        else:	#user is subscribed
            db_exp = conn[exp_name]

            #updates the last_interaction so the question will be asked in the next round
            db_fbuser.user.update_one({"fbid":fbid},
                                      {"$set":{"last_interaction":datetime.today()}},
                                       upsert=False
                                     )

            #start the process to ask questions
            begin_questions(exp_name)

#start the process to ask questions to users
def begin_questions(exp_name):
    
    #create a connection with database
    db_exp = conn[exp_name] 

    option_list = ssc_config.begin_options
    text = ssc_config.begin_text

    #for all registered users
    for user in db_fbuser.user.find():

        #if it has passed enough time since the last user's interaction with the bot and the user is active
        if datetime.today() > user['last_interaction'] + timedelta(days=user['next_interaction']) and user['active']:
            sts,msg = post_quick_reply(user['fbid'],text,option_list,'begin_question#'+exp_name,None)

            #update last interaction date
            if sts:
                db_fbuser.user.update_one({"fbid":user['fbid']},{"$set":{"last_interaction":datetime.today()}},upsert=False)

#ask questions for a specific user
def ask_question(exp_name,fbid):

    db_exp = conn[exp_name]

    asked_schedule_id = []

    #for each question already asked for a specific user
    for question in db_exp.question.find({"recipient.id":fbid}):
        asked_schedule_id.append(ObjectId(question['identifier']))

    #find one question that was not asked
    schedule = db_exp.schedule.find_one({"_id":{"$nin": asked_schedule_id}})

    #if there are still questions that were not asked for this user
    if schedule is not None:

        #post question statement
        sts1,msg1 = post_simple_message(fbid,schedule['question'].replace("*","\n"))

        #if the statement question worked
        if sts1:

            #ask the quick reply question 
            sts2,msg2 = post_quick_reply(fbid,
                                         ssc_config.reply_text,
                                         ssc_config.reply_options,
                                         'get_answer#'+exp_name+'#'+str(schedule['_id']),
                                         str(schedule['_id'])
                                        )

            #if the quick reply question worked
            if sts2:

	        #insert the question into the database
	        db_exp.question.insert_one(json.loads(msg2))

    else:	#there are no more questions to ask
        post_simple_message(fbid,ssc_config.no_more_questions)

def record_answer(exp_name,schedule_id,answer):

    db_exp = conn[exp_name]
    
    db_exp.answer.insert_one({"schedule_id":ObjectId(schedule_id),"answer":answer})

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-b","--build", action='store_true')
    parser.add_argument("-e","--experiment", action='store')
    parser.add_argument("-qf","--questionfile", action='store')
    parser.add_argument("-a","--askquestions", action='store_true')

    args = parser.parse_args()

    if args.build:
        build_experiment(args.experiment,args.questionfile)
    elif args.askquestions:
        
        #check whether the experiment is active
        if args.experiment in ssc_config.active_experiments:
            begin_questions(args.experiment)
        else:
            print "The experiment "+args.experiment+" is not active or does not exist"
