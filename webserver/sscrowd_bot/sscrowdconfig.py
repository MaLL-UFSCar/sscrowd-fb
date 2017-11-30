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
        self.reply_options = config.get('SSCrowd-FB','reply_options')
        self.db_address = config.get('MongoDB','db_address')
        
