#this file contains the SS-Crowd tools to interact with Facebook Messenger

import sys
import os
import argparse
import json

from datetime import datetime
from utils import post_quick_reply
from utils import post_simple_message
from sscrowdconfig import ConfigSSCrowdFB

from datetime import datetime

from pymongo import MongoClient
from pymongo import database

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
            

def verify_user(db_exp,user,schedule):

    verify = False

    #if this scheduled question has already been asked to this user
    if db_exp.question.find({"recipient.id":user['fbid'],"schedule_id":str(schedule['_id'])}).count() == 0:

        #get the next interaction date
        next_interaction_date = datetime.strptime(user['next_interaction'],'%Y%m%d%H%M%S')

        #if next interaction date has already passed
        if datetime.today() > next_interaction_date:
             verify = True

    return verify

def ask_questions(exp_name):

    db_exp = conn[exp_name]
    db_users = conn['fbusers']

    #for all scheduled questions 
    for schedule in db_exp.schedule.find():

        #for all registered users
        for user in db_users.users.find():

            #check constraint to ask specific scheduled question to specific user
            if verify_user(db_exp,user,schedule):

                ssc_config = ConfigSSCrowdFB()

                #ask the simple question
                sts1,msg1 = post_simple_message(user['fbid'],ssc_config.statement)
                 
                #if the simple question worked
                if sts1:

                    #ask the quick reply question 
                    sts2,msg2 = post_quick_reply(user['fbid'],str(schedule['_id']))

                    #if the quick reply question worked
                    if sts2:

                        #insert the question into database
                        db_exp.question.insert_one(json.loads(msg2))

                        db_users.users.update_one({"fbid":user['fbid']},{'$next_interaction")

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
        ask_questions(args.experiment)
        

