'''
Created on 2019. 5. 8.

@author: Administrator
'''



#!/usr/bin/env python

import pyVmomi
import argparse
import atexit
import itertools
import configparser
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect
import humanize
import ssl
from datetime import datetime, timedelta
import os
import sys
import fletaSnmp


MBFACTOR = float(1 << 20)

printVM = False
printDatastore = True
printHost = False


class vcEvent():
    def __init__(self):
        self.snmp = fletaSnmp.Load()
    
    def getList(self):
        vcList=[]
        cfg=configparser.RawConfigParser()
        cfgFile=os.path.join('config','list.cfg')
        cfg.read(cfgFile)
        print cfgFile,os.path.isfile(cfgFile)
        for sec in cfg.sections():
            vcInfo={}
            vcInfo['name']=sec
            for opt in cfg.options(sec):
                vcInfo[opt] = cfg.get(sec,opt)
            vcList.append(vcInfo)
            print vcInfo
        return vcList

    def fwrit(self,msg,wbit='a'):
        with open('alarm.txt',wbit) as f:
            f.write(msg+'\n')
    def alarm(self,host,user,passwd):
        
        host='121.170.193.209'
        user='administrator@vsphere.local'
        password='Kes2719!'
        
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
            si = SmartConnect(host=host,
                          user=user,
                          pwd=passwd,
                          port=50000,
                          sslContext=context)
        
        
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        am = content.alarmManager
        alarms = am.GetAlarm(content.rootFolder) # get all alarms
        print ('###***vcenter_event list***###','w')
        alarmList=[]
        
        searchIndex = si.RetrieveContent().searchIndex
        vim = searchIndex.FindAllByIp(ip=host, vmSearch=True)

       
# #         sys.exit()
#         for alarm in alarms:
#             print alarm.info
#             alarmList.append(alarm)
#             try:
#                 # only alarms of type EventAlarms can be unset
#                 if isinstance(alarm.info.expression.expression[0], vim.alarm.EventAlarmExpression):
#                     # status can be Normal, Warning, Alert, or Unset. Unset maps to "none"
#                     if alarm.info.expression.expression[0].status == None:
#                         print '-'*50
#                         errDic={}
# #                         print alarm.info
#                         print alarm.info.name
#                         print alarm.info.description
#                         print alarm.info.systemName
#                         timestr= alarm.info.lastModifiedTime
#                         event_time= timestr.strftime('%Y-%m-%d %H:%M:%S')
#                         errDic={}
#                         errDic['serial']=host
#                         errDic['event_date']=event_time
#                         errDic['event_code']=alarm.info.name
#                         errDic['severity']='Alarm'
#                         errDic['desc']=alarm.info.description
#                         errDic['vendor']='VMware'
#                         errDic['device_type']='vCenter'
#                         errDic['method'] = 'snmp'
#                         errDic['etc'] =alarm.info.systemName
#                         self.snmp.errSnmpTrapSend(errDic)
#                         self.fwrite(alarm.info)
#             except AttributeError, e:
#                 None



        return alarmList
    
    
    def getDtime(self):
        dfile=os.path.join('config','dTime.txt')
        
        if os.path.isfile(dfile):
            with open(dfile)as f:
                dtime=f.read()
        else:
            dtime=''
        return dtime
    
    
    
    def main(self):
        
        print 'START'
        vcList=self.getList()
        startTime=''
        for vcInfo in vcList:
            print vcInfo
            host=vcInfo['ip']
            user=vcInfo['username']
            passwd=vcInfo['password']
            alarms=self.alarm(host, user, passwd)
            with open('%s_txt'%host,'w') as f:
                for alarm in alarms:
                    print dir(alarm)
                    print alarm.Array
                    print (str(alarm.info))
                    
if __name__ == "__main__":
    """
        errDic={}
        errDic['serial']='11111'
        errDic['event_date']='2019-05-16 15:00:01'
        errDic['event_code']='0x1234'
        errDic['severity']='Warning'
        errDic['desc']='test'
        errDic['vendor']='VMware'
        errDic['device_type']='vCenter'
        errDic['method'] = 'snmp'
        errDic['etc'] ='test'
    """
    print vim.host.DateTimeSystem.TimeZone.Array()
    print dir(vim.host.DateTimeSystem.TimeZone)
    vcEvent().main()
