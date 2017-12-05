#this file contains the SS-Crowd tools to interact with Facebook Messenger

import sys
import os
import argparse
import json
import pymongo
import pprint

from datetime import datetime
from utils import post_quick_reply
from utils import post_simple_message
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

def build_experiment(exp_name,question_file):

    db_exp = conn[exp_name]

    schedule(db_exp,question_file)

def schedule(db_exp,question_file):

    with open(question_file,'r') as ql_raw:

        #for all questions in the question file
        for question in ql_raw:

            #try to schedule the question
            try:
                db_exp.schedule.insert_one({"question":question})
            except pymongo.errors.DuplicateKeyError:
                pass
            

def create_user(fbid):

    db_fbuser = conn['fbuser']

    #sets fbid to be unique
    db_fbuser.user.create_index([('fbid',pymongo.ASCENDING)], unique=True)

    #try to insert the new user
    try:
        db_fbuser.user.insert_one(
	    {
	        'fbid':fbid,
	        'last_interaction':datetime.today(),
	        'active':True
	    },
        )
    except pymongo.errors.DuplicateKeyError:
        pass

def handle_message(message):

    pprint.pprint(message)

    fbid = message['sender']['id']

    #try to create user
    create_user(fbid)

    message_obj = message['message']

    #if the message is an option of a SS-Crowd quick reply
    if message_obj.has_key('quick_reply'):

        handler = message['message']['quick_reply']['payload'].split('#')
        option = message['message']['text']

        action = handler[0]	#the action to be performed by this handler
        exp_name = handler[1]	#the name of the experiment

        
        if action == 'begin_question':		#the user agreed to answer questions
            if option == 'Yes':
                #ask the first question
                ask_question(exp_name,fbid)
            elif option == 'No':
                #send message to user and leave program
                post_simple_message(fbid,ssc_config.no_begin_answer)

        elif action == 'get_answer':	#the user sent an answer
            print "getting answer"

            schedule_id = handler[2]
             
            #save the answer
            record_answer(exp_name,schedule_id,option)

            #keep asking questions
            ask_question(exp_name,fbid)
    else:
        #the user only interacts through quick reply
        post_simple_message(fbid,ssc_config.no_quick_reply_answer)
        
    
#start the process to ask questions to users
def begin_questions(exp_name):
    
    #create a connection with database
    db_exp = conn[exp_name] 
    db_user = conn['fbuser']

    option_list = ssc_config.begin_options
    text = ssc_config.begin_text

    #for all registered users
    for user in db_user.user.find():

        #if it has passed enough time since the last user's interaction with the bot
        if datetime.today() > user['last_interaction'] + timedelta(days=0):
            sts,msg = post_quick_reply(user['fbid'],text,option_list,'begin_question#'+exp_name,None)

            #update last interaction date
            if sts:
                db_user.user.update_one({"fbid":user['fbid']},{"$set":{"last_interaction":datetime.today()}},upsert=False)

#ask questions for a specific user
def ask_question(exp_name,fbid):

    db_exp = conn[exp_name]
    db_users = conn['fbusers']

    user = db_users.users.find({"fbid":fbid})

    asked_schedule_id = []

    #TODO there has to be a maximum of questions a person can answer in a short time

    #for each question already asked for a specific user
    for question in db_exp.question.find({"recipient.id":fbid}):
        asked_schedule_id.append(ObjectId(question['identifier']))

    #find one question that was not asked
    schedule = db_exp.schedule.find_one({"_id":{"$nin": asked_schedule_id}})

    #if there are still questions that were not asked for this user
    if schedule is not None:

        #post question statement
        sts1,msg1 = post_simple_message(fbid,ssc_config.statement)

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
    else:
        post_simple_message(fbid,ssc_config.no_more_questions)

def record_answer(exp_name,schedule_id,option):
    print exp_name
    print schedule_id
    print option


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
        begin_questions(args.experiment)
        

