
import sys
import logging

from app.configurations import LoggingConfig
from app.metaclasses_definition import Singleton
from app.configurations import LoggingDestination

from logging.handlers import RotatingFileHandler

def init_logger():

    logger = logging.getLogger(__name__)
    logger.setLevel(LoggingConfig.level)
    
    if LoggingConfig.destination == LoggingDestination.File:
        destHandler = RotatingFileHandler(
            LoggingConfig.filepath, 
            maxBytes=LoggingConfig.maxBytes, 
            backupCount=LoggingConfig.backupCount
        )
    else:
        destHandler = logging.StreamHandler()
    
    format = '%(asctime)s - %(module)s:%(lineno)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format)
    destHandler.setFormatter(formatter)
    logger.addHandler(destHandler)

    return logger

log = init_logger()
