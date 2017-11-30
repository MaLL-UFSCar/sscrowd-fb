#this is script contains the essential configuration
#for the sscrowd-fb algorithm. It should be run right
#after cloning the repository

from pymongo import MongoClient

conn = MongoClient('mongodb://localhost:27017')
fb_db = conn['fbuserst']

fb_db.create_collection('users')

fb_db.users.createIndex({"fbid":1},unique=True)
