# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

# Create your models here.

class UserStatus():
    def __init__(self,fbid):

        self.fbid = fbid
        
        self.status_file = settings.EXPERIMENTS_DIR+'/data/status/'+self.fbid
        print self.status_file
