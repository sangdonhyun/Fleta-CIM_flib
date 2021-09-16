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

        for sec in cfg.sections():
            vcInfo={}
            vcInfo['name']=sec
            for opt in cfg.options(sec):
                vcInfo[opt] = cfg.get(sec,opt)
            vcList.append(vcInfo)

        return vcList

    def set_dtime(self,host):
        try:
            dtime_file = os.path.join('config', '{}_alm_dtime.txt'.format(host))
            with open(dtime_file,'w') as fw:
                fw.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            with open(dtime_file, 'r') as fw:
                print fw.read()
        except:
            pass

    def get_dtime(self,host):
        dtime_file = os.path.join('config','{}_alm_dtime.txt'.format(host))
        if os.path.isfile(dtime_file):
            try:
                with open(dtime_file) as f:
                    rf= f.read()
                    dtime = datetime.strptime(rf,'%Y-%m-%d %H:%M:%S')
            except Exception as e:
                dtime = datetime.now()-timedelta(days=7)
        else:
            dtime = datetime.now()-timedelta(days=7)
        return dtime


    def fwrite(self,msg,wbit='a'):
        with open('alarm.txt',wbit) as f:
            f.write(msg+'\n')
    def alarm(self,host,user,passwd,port):


#         host='10.10.10.64'
#         user='administrator@vsphere.local'
#         password='Kes2719!'
        
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
            si = SmartConnect(host=host,
                          user=user,
                          pwd=passwd,
                          port=port,
                          sslContext=context)
        
        
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        am = content.alarmManager
        alarms = am.GetAlarm(content.rootFolder) # get all alarms
        print ('###***vcenter_event list***###','w')
        alarmList=[]
        
        searchIndex = si.RetrieveContent().searchIndex
        vms = searchIndex.FindAllByIp(ip=host, vmSearch=True)
        errList= []
        dtime = self.get_dtime(host)
#         
        self.fwrite('','w')
        # print 'dtime : ',dtime,type(dtime)
        for alarm in alarms:
            # print '-'*50
            # print alarm
            # print '-' * 50
            alarmList.append(alarm)
            try:
                # only alarms of type EventAlarms can be unset
                if isinstance(alarm.info.expression.expression[0], vim.alarm.EventAlarmExpression):
                    # status can be Normal, Warning, Alert, or Unset. Unset maps to "none"
                    if alarm.info.expression.expression[0].status == None:

                        errDic={}
#                         print alarm.info

                        timestr= alarm.info.lastModifiedTime
                        event_time= timestr.strftime('%Y-%m-%d %H:%M:%S')

                        event_time_dt = datetime.strptime(event_time,'%Y-%m-%d %H:%M:%S')

                        errDic={}
                        errDic['serial']=host
                        errDic['event_date']=event_time
                        errDic['event_code']=alarm.info.name
                        errDic['severity']='Alarm'
                        errDic['desc']=alarm.info.description
                        errDic['vendor']='VMware'
                        errDic['device_type']='VCT'
                        errDic['method'] = 'snmp'
                        errDic['etc'] =alarm.info.systemName
                        # print event_time_dt > dtime,event_time_dt,dtime
                        if event_time_dt > dtime:
                            errList.append(errDic)
                            self.snmp.errSnmpTrapSend(errDic)
                            # self.fwrite(str(alarm.info))

            except AttributeError, e:
                None



        return errList
    
    
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

            host=vcInfo['ip']
            user=vcInfo['username']
            passwd=vcInfo['password']
            port = vcInfo['port']
            errList=self.alarm(host, user, passwd,port)
            print ('err list  count :',len(errList))
            # for err in errList:
            #     print err
            self.set_dtime(host)
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
    # print vim.host.DateTimeSystem.TimeZone.Array()
    # print dir(vim.host.DateTimeSystem.TimeZone)
    vcEvent().main()
