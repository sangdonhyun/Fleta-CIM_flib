#-*- coding: utf-8 -*
'''
Created on 2019. 10. 11.

@author: Administrator
'''

import logging
import os
import datetime
def flog():
    logName='event_sms.log'
    LOG_FILENAME = os.path.join('log','%s'%logName)
    logger=logging.getLogger('eventlog')
    if not len(logger.handlers):
        logger.setLevel(logging.DEBUG)
        now = datetime.datetime.now()
        handler=logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger