'''
Created on 2012. 10. 12.

@author: Administrator
'''
'''
Created on 2012. 9. 27.

@author: Administrator
'''
import sys
import os
import datetime
import time
import configparser
from ftplib import FTP
import re
import logging
import glob
import logging.handlers
import base64
import hashlib




class Decode():
    
    def _en(self,_in) : return base64.b64encode(_in) 
    
    def _de(self,_in) : return base64.b64decode(_in)
    
    def fenc(self,str):
        e0  = self._en(str)
        e1  = self._en(e0)
        m   = hashlib.md5(e0).hexdigest()
        e1 = e1.replace('=','@')
        e = e1 + '@' + m
        return e
    
    def fdec(self,e):
        r = e.rfind('@')
        if r == -1:
            pass
        d1  = e[:r]
        d1  = d1.replace('@','=')
        d0  = self._de( d1 );
        d   = self._de( d0 );
        return d

    def decBit(self,fileName):
        with open(fileName) as f:
            tmp = f.read()
        if re.search('###\*\*\*',tmp):
            return True
        else:
            return False
    
    def fileDec(self,fileName):
        if self.decBit(fileName):
            return None
        with open(fileName) as f:
            str = f.read()
        with open(fileName,'w') as f:
            f.write(self.fdec(str))
        return self.decBit(fileName)
    
    def fileDecReText(self,fileName):
        if self.decBit(fileName):
            with open(fileName) as f:
                reList = f.read()
            
        else:
            with open(fileName) as f:
                str = f.read()
            reList = self.fdec(str)
        
        return reList
        
    
    def fileEncDec(self,fileName):
        if self.decBit(fileName)==False:
            return None
        with open(fileName) as f:
            str = f.read()
        with open(fileName,'w') as f:
            f.write(self.fenc(str))
        return self.decBit(fileName)
    
    
        
class Common():
    def __init__(self):
        self.curDir = self.cuDir()
        self.logDir = os.path.join(self.curDir,'log')
        self.confDir = os.path.join(self.curDir,'config')
        self.dataDir = os.path.join(self.curDir,'data')
        self.hitachiConfig()
        self.server,self.user,self.passwd=None,None,None
        self.cfg = self.getCfg()
        self.env = os.environ
        self.logger = self.flog()

        
    def hitachiConfig(self):
        if os.path.isdir(self.logDir) == False:
            os.mkdir(self.logDir) 
        if os.path.isdir(self.confDir) == False:
            os.mkdir(self.confDir)
        if os.path.isdir(self.dataDir) == False:
            os.mkdir(self.dataDir)
    
    def getCfg(self):
        
        cfgFile = os.path.join(self.confDir,'config.cfg')
        if os.path.isfile(cfgFile) == False:
            self.sysOut('cfg file problem')
        config = configparser.RawConfigParser()
        config.read(cfgFile)
        # self.server=config.get('server','ip')
        # self.user=config.get('server','user')
        # if len(config.get('server','passwd')) > 40:
        #     self.passwd=Decode().fdec(config.get('server','passwd'))
        # else:
        #     self.passwd=config.get('server','passwd')
        return config
    
    
    
    def flog(self):
        try:
            logName=os.path.dirname( os.path.abspath( 'config' ) ).split('\\')[-1]
        except:
            logName='fleta.log'
        LOG_FILENAME = os.path.join(self.logDir,'%s.log'%logName)
#        if None == self.logger:
#            self.logger=logging.getLogger('fleta')
#            self.logger.setLevel(logging.DEBUG)
#            now = datetime.datetime.now()
#            handler=logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=3)
#            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#            handler.setFormatter(formatter)
#            self.logger.addHandler(handler)
#        return self.logger
        logger=logging.getLogger('fleta')
        if not len(logger.handlers):
            logger.setLevel(logging.DEBUG)
            now = datetime.datetime.now()
            handler=logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=3)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    

    
    def sysOut(self,msg):
        logger = self.flog()
        logger.info(msg)
        sys.stdout.write(msg+'\n')
    
    def cuDir(self):
        frozen = getattr(sys, 'frozen', '')
        if not frozen:
            # not frozen: in regular python interpreter
            try:
                approot = os.path.dirname('common.py')
            except:
                pass
                
        elif frozen in ('dll', 'console_exe', 'windows_exe'):
            # py2exe:
            approot = os.path.dirname(sys.executable)
       
        elif frozen in ('macosx_app',):
            # py2app:
            # Notes on how to find stuff on MAC, by an expert (Bob Ippolito):
            # http://mail.python.org/pipermail/pythonmac-sig/2004-November/012121.html
            approot = os.environ['RESOURCEPATH']
        return approot
    
    def getNow(self,format='%Y-%m-%d %H:%M:%S'):
        return time.strftime(format)

    def getHeadMsg(self,title='FLETA BATCH LAOD'):
        now = self.getNow()
        msg = '\n'
        msg += '#'*79+'\n'
        msg += '#### '+' '*71+'###\n'
        msg += '#### '+('TITLE     : %s'%title).ljust(71)+'###\n'
        msg += '#### '+('DATA TIME : %s'%now).ljust(71)+'###\n'
        msg += '#### '+' '*71+'###\n'
        msg += '#'*79+'\n'
        return msg
    
    def getEndMsg(self):
        now = self.getNow()
        msg = '\n'
        msg += '#'*78+'\n'
        msg += '####  '+('END  -  DATA TIME : %s'%now).ljust(69)+'###\n'
        msg += '#'*78+'\n'
        return msg
    


def logTest():
    common = Common()
    logger=common.flog()
    logger.info('log test')
    
    

if __name__=='__main__':
#    logTest()
#    fname=os.path.join('data','fs_ibk-test05.tmp')
#    print os.path.isfile(fname)
#    print Common().fletaPutFtp(fname,'diskinfo.SCH')
    dec=Decode()
    print(dec._en('kes2719!'))
    print(dec._de('a2VzMjcxOSE'))

    
    
    
