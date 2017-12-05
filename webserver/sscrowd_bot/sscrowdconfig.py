#this configuration class holds basic attributes to
#configure SSCrowd, the Facebook Messenger API
#and the Mongo DB for this appplication

import ConfigParser

class ConfigSSCrowdFB():

    def __init__(self):

        config = ConfigParser.ConfigParser()
        config.read('conf/sscrowd-fb.conf')

        self.statement = config.get('SSCrowd-FB','statement')
        self.access_token = config.get('Facebook-Messenger-API','access_token')
        self.reply_options = config.get('SSCrowd-FB','reply_options').split(';')
        self.reply_text = config.get('SSCrowd-FB','reply_text')
        self.db_address = config.get('MongoDB','db_address')
        self.begin_options = config.get('SSCrowd-FB','begin_options').split(';')
        self.begin_text = config.get('SSCrowd-FB','begin_text')

        self.no_begin_answer = config.get('SSCrowd-FB','no_begin_answer')
        self.no_quick_reply_answer = config.get('SSCrowd-FB','no_quick_reply_answer')
        self.no_more_questions = config.get('SSCrowd-FB','no_more_questions')
        
        
