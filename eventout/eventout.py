'''
Created on 2017. 10. 16.

@author: muse
'''
import os
import sys
import configparser
import zipfile
import glob
import common
import fletaDbms
import datetime
import time

class Load():
    def __init__(self):
    
        self.cfg = self.getCfg()
        self.db = fletaDbms.FletaDb()
        self.com= common.Common()
        self.td =  self.com.getNow('%Y%m%d')
        self.todayTable = self.getTableName(self.td)
        os.environ['PGPASSWORD']=self.cfg.get('database','password')
        self.dfile=os.path.join('config','dtime.txt')
    
    def getTableName(self,date):
        return 'pm_auto_hitachi_real_info_%s'%date
    
    def getCfg(self):
        cfg = configparser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg
    
    
    def getEventListQuery(self,dev,dtime):
        if dev=='sfp':
            query = """
select event_date, vendor_name, serial_number, q_event_level,desc_summary from event.event_log where (event_code like 'SWI.MON.SFP.TX%' or event_code like 'SWI.MON.SFP.RX%') and user_id = ''  and check_date > '"""+dtime+"""' order by 1
"""
        elif dev=='crc':
            query = """
select event_date, vendor_name, serial_number, q_event_level,desc_summary from event.event_log where (event_code like 'SWI.MON.CRC%') and user_id =  ''  and event_date > '"""+dtime+"""' order by 1
"""
        else:
            query = """
select event_date, vendor_name, serial_number, q_event_level,desc_summary from event.event_log where (event_code like 'SWI.MON.CRC%') and user_id =  ''  and event_date > '"""+dtime+"""' order by 1
"""
        crclist=self.db.getRaw(query)
        return crclist
            
    def CrcQuery(self,dtime):
        crcquery = """
select event_date, vendor_name, serial_number, q_event_level,desc_summary from event.event_log where (event_code like 'SWI.MON.CRC%') and user_id =  ''  and event_date > '"""+dtime+"""' order by 1
"""
        crclist=self.db.getRaw(crcquery)
        return crclist


    def SfpQuery(self,dtime):
        
#         print dtime
        crcquery = """
select event_date, vendor_name, serial_number, q_event_level,desc_summary from event.event_log where (event_code like 'SWI.MON.SFP.TX%' or event_code like 'SWI.MON.SFP.RX%') and user_id = ''  and check_date > '"""+dtime+"""' order by 1
"""
        crclist=self.db.getRaw(crcquery)
        return crclist
    
    def setDtime(self,dtime):
        with open(self.dfile,'w') as f:
            f.write(dtime)
   
    def getDtime(self,fname):
        try:
            with open(fname) as f:
                tmp2=f.readlines()
            targettime= tmp2[-1].split(']')[0].replace('[','')
            
            targetdatetime=datetime.datetime.strptime(targettime,"%Y-%m-%d %H:%M:%S")
            dtime=unicode(targetdatetime)
        except:
            dtime=time.strftime('%Y-%m-%d 00:00:00')
        
        
        print 'dtime :',dtime
        return dtime
    
    def getFileName(self,ven,dev):
        opt= '%s_%s'%(ven,dev)
        fname=self.cfg.get('eventout',opt)
        return fname
    
    def fileWrite(self,ven,dev,msg):
        opt='%s_%s'%(ven,dev)
        fname=self.getFileName(ven, dev)
        with open(fname,'a') as f:
            f.write(msg+'\n')

    def main(self):
    
        
        headmsg=self.com.getHeadMsg('SAN SWITCH EVENT OUT')
        print headmsg
#         self.crcSet()
#         self.sfpSet() 
        self.setFile()
        print self.com.getEndMsg() 
        
    def setFile(self):
        opts=self.cfg.options('eventout')
        
        for opt in opts:
            print opt         
            fname=self.cfg.get('eventout',opt)
            print fname
            ven,dev=opt.split('_')
            print ven,dev
            dtime=self.getDtime(fname)
            sfpList=self.getEventListQuery(dev,dtime)
            for sfp in sfpList:
                date= sfp[0].strip()
                level= sfp[3].strip()
                msg=sfp[4].strip()
    #             msg= """[%s][%s] %s """%(date,level,msg)
                print msg
                serial = sfp[3]
                ven=self.getVendor(serial)
                self.fileWrite(ven,'sfp', msg)
                
            
    def sfpSet(self):
        
        fname=self.cfg.get('eventout','sfp')
        dtime=self.getDtime(fname)
        sfpList=self.SfpQuery(dtime)
        print 'SFP MESSAGE COUNT :',len(sfpList)
        for sfp in sfpList:
            date= sfp[0].strip()
            level= sfp[3].strip()
            msg=sfp[4].strip()
#             msg= """[%s][%s] %s """%(date,level,msg)
            print msg
            serial = sfp[3]
            ven=self.getVendor(serial)
            self.fileWrite(ven,'sfp', msg)
    
    def getVendor(self,serial):
        sql="select swi_serial, swi_contract_info[2] supplier from master.master_swi_info where swi_serial = '%s'"%serial
        ret=self.db.getRaw(sql)
        ven=ret[0][0]
        return ven
        
    def crcSet(self):
        fname=self.cfg.get('eventout','crc')
        dtime=self.getDtime(fname)
        print 'LAST CRC DATETIME :',dtime
        crcList=self.CrcQuery(dtime)
        print 'CRC MESSAGE COUNT :',len(crcList)
        
        
        
        for crc in crcList:
            date= crc[0].strip()
            level= crc[3].strip()
            msg=crc[4].strip()
            msg= """[%s][%s] %s """%(date,level,msg)
            print msg
            serial=crc[3]
            ven=self.getVendor(serial)
            self.fileWrite(ven,'crc', msg)
        

if __name__=='__main__':
    Load().main()
#     while True:
#         load=Load()
#         try:
#             delay=load.cfg.get('common','sleep')
#             delay=int(delay)
#         except:
#             delay=600
#         load.main()
#          
#         print 'SLEEP %s sec'%delay
#         time.sleep(delay)
