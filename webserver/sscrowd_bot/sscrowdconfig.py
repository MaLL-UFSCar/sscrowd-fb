#this configuration class holds basic attributes to
#configure SSCrowd, the Facebook Messenger API
#and the Mongo DB for this appplication

import ConfigParser

class ConfigSSCrowdFB():

    def __init__(self):

        config = ConfigParser.ConfigParser()
        config.read('conf/sscrowd-fb.conf')

        self.access_token = config.get('Facebook-Messenger-API','access_token')

        self.db_address = config.get('MongoDB','db_address')


        self.reply_options = config.get('SSCrowd-FB','reply_options').split(';')
        self.reply_text = config.get('SSCrowd-FB','reply_text')

        self.begin_options = config.get('SSCrowd-FB','begin_options').split(';')
        self.begin_text = config.get('SSCrowd-FB','begin_text')
        self.no_begin_answer = config.get('SSCrowd-FB','no_begin_answer')

        self.ask_one_more_text = config.get('SSCrowd-FB','ask_one_more_text')
        self.ask_one_more_options = config.get('SSCrowd-FB','ask_one_more_options').split(';')
        self.no_more_answers = config.get('SSCrowd-FB','no_more_answers')

        self.no_quick_reply_answer = config.get('SSCrowd-FB','no_quick_reply_answer')
        self.no_more_questions = config.get('SSCrowd-FB','no_more_questions')

        self.active_experiments = config.get('SSCrowd-FB','active_experiments').split(';')

        self.subscribe_options = config.get('SSCrowd-FB','subscribe_options').split(';')
        self.subscribe_text = config.get('SSCrowd-FB','subscribe_text')
        self.subscribe_answer = config.get('SSCrowd-FB','subscribe_answer')

        self.no_subscribe_answer = config.get('SSCrowd-FB','no_subscribe_answer')
        self.unsubscribe_answer = config.get('SSCrowd-FB','unsubscribe_answer')
        
        
        
