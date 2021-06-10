
import sys
import logging

from enum import Enum

class MongoConfig:

    url = "mongodb://172.17.0.3:27017"
    username = None
    password = None

class LoggingDestination(Enum):

    Console = 1
    File = 2

class LoggingConfig:

    stream = sys.stdout
    
    filepath = "./logs/evalsr.log"
    maxBytes = 8*1024*1024
    backupCount = 10
    level = logging.DEBUG
    
    destination = LoggingDestination.Console

class AngelBrokingConfig:

    apiKey = "BAIUxGLc"
    username = "D85774"
    password = "$Stock@2100"
