   
'''
Created on 2019. 7. 9.

@author: Administrator
'''

import atexit
from pyVim import connect
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi.VmomiSupport import Object, DataObject, F_LINK, F_LINKABLE, F_OPTIONAL, F_SECRET, ManagedObject
from pyVmomi.VmomiSupport import UncallableManagedMethod, ManagedMethod, binary, Iso8601
from pyVmomi import vmodl
from pyVmomi import vim
import base64
import json
import codecs
import sys
import chardet
import re
import datetime
import os
import fletaSnmp
import ConfigParser

class VM():
    def __init__(self,vmInfo):
        self.host = vmInfo['ip']
        self.user = vmInfo['username']
        self.passwd=vmInfo['password']
        self.snmp=fletaSnmp.Load()
        self.alarmListFile=os.path.join('list','alarmlist.txt')
        self.eventListFile=os.path.join('list','eventlist.txt')
        if not os.path.isfile(self.alarmListFile):
            self.setOldAlarmList(self.alarmListFile,'', 'w')
        if not os.path.isfile(self.eventListFile):
            self.setOldAlarmList(self.eventListFile,'', 'w')


    def getErrDic(self,alarm,trAlarm):
        alarmInfo=alarm.info
        errDic={}
        errDic['serial']=self.host
        if trAlarm == None:
            errDic['event_date']=alarmInfo.lastModifiedTime.strftime('%Y-%m-%d %H:%M:%S')
            errDic['severity']='yellow'
        else:
            errDic['event_date']=trAlarm.time.strftime('%Y-%m-%d %H:%M:%S')
            errDic['severity']= trAlarm.overallStatus
            
        errDic['event_code']=alarmInfo.key
        
        errDic['desc']=alarmInfo.description
        errDic['vendor']='VMware'
        errDic['device_type']='VCT'
        errDic['method'] = 'snmp'
        errDic['etc'] ='%s %s'%(alarmInfo.alarm,alarmInfo.name)
        return errDic

   
    
    def getOldAlarmList(self,filename):
        with open(filename,'r') as f:
            tmp =f.read().split()
        return tmp
    
    def setOldAlarmList(self,filename,alarm,wbit='a'):
        
        with open(filename,wbit) as f:
            f.write(alarm+'\n')
        
    def GetVMHosts(self,content):
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj        
    
    def getHostAlarm(self,hosts):
        hostAlarms=[]
        for host in hosts:
            alarms = host.triggeredAlarmState
            for alarm in alarms:
                print alarm
                hostAlarms.append(alarm)
        return hostAlarms
    
    def getAttrAlarm(self,hostAlarms,alname):
        for alarm in hostAlarms:
            if unicode(alarm.alarm) == alname:
                return alarm
                break
        return None
    def VmAlarmManager(self,content):
        am = content.alarmManager
        alarms = am.GetAlarm(content.rootFolder)
        
        hosts=self.GetVMHosts(content)
        hostAlarms=self.getHostAlarm(hosts)
        
#         for hostAlarm  in hostAlarms:
#             print hostAlarm
#         
        
        
        alList=self.getOldAlarmList(self.alarmListFile)
        print 'TOT CNT :',len(alarms)
        for alarm in alarms:
            alname=unicode(alarm)
            trAlarm=self.getAttrAlarm(hostAlarms, alname)
            self.getAttrAlarm(hostAlarms, alname)
            if alname not in alList:
                dict=self.getErrDic(alarm,trAlarm)
                print dict
                self.snmp.errSnmpTrapSend(dict)
                self.setOldAlarmList(self.alarmListFile,alname)
    
    def VmEventManager(self,si,content):
        
        oldevlist=self.getOldAlarmList(self.eventListFile)
            # A list comprehension of all the root folder's first tier children...
        datacenters = [entity for entity in content.rootFolder.childEntity
                                  if hasattr(entity, 'vmFolder')]
        for dc in datacenters:
    

            
            ids = ['VmRelocatedEvent', 'DrsVmMigratedEvent', 'VmMigratedEvent']
            
            
            ids = ['VmRelocatedEvent', 'DrsVmMigratedEvent', 'VmMigratedEvent']
#             filterSpec = vim.event.EventFilterSpec(entity='', eventTypeId=ids)
            event_type_list = []
            filterSpec = vim.event.EventFilterSpec(eventTypeId=event_type_list)
            # Optionally filter by users
            
            
            eventManager = si.content.eventManager
            event_collector = eventManager.CreateCollectorForEvents(filterSpec)
#             events = eventManager.QueryEvent(filterSpec)
            events = event_collector.latestPage
        
            for event in events:
                typeSet= str(type(event))
                eventType=typeSet.split('.')[-1]
                eventType=eventType.replace("'>",'')
                
                key=str(event.key)
#                 print key not in oldevlist
                print eventType
                if eventType not in  ['UserLoginSessionEvent','UserLogoutSessionEvent']:
                    if key not in oldevlist:
                        if eventType == 'TaskEvent':
                            desc='%s '
                        print ('-'*30)
                        
                        print (event.chainId)
                        print (event.userName)
                        
                        try:
                            print (event.createdTime.strftime('%Y-%m-%d %H:%M:%S'))
                        except:
                            print ('createtime error')
                        print event.fullFormattedMessage
                        errDic={}
                        errDic['serial']=self.host
                        errDic['event_date']=event.createdTime.strftime('%Y-%m-%d %H:%M:%S')
                        errDic['event_code']=str(event.key)
                        errDic['severity']='green'
                        errDic['desc']=event.fullFormattedMessage
                        errDic['vendor']='VMware'
                        errDic['device_type']='VCT'
                        errDic['method'] = 'snmp'
                        errDic['etc'] =eventType
                        self.snmp.errSnmpTrapSend(errDic)
                        self.setOldAlarmList(self.eventListFile, key)
                        print errDic
    def main(self):
        si = SmartConnectNoSSL(host=self.host,
                               user=self.user,
                               pwd=self.passwd,
                               port=443)
        content = si.RetrieveContent()
            # A list comprehension of all the root folder's first tier children...
        
        self.VmAlarmManager(content)
        self.VmEventManager(si,content)

class Manager():
    def __init__(self):
        self.cfg = self.getCFg()
    
    
    def getCFg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile= os.path.join('config','list.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def getHost(self):
        hostList=[]
        for sec in self.cfg.sections():
            host={}
            host['name'] = sec
            
            for opt in self.cfg.options(sec):
                host[opt] = self.cfg.get(sec,opt)
            hostList.append(host)
        return hostList
    
    
    def main(self):
        hostList=self.getHost()
        for host in hostList:
            VM(host).main()
 
            
if __name__ == "__main__":
    import time
    Manager().main()
#     print 'alarm monitor start...'
#     while True:
#         print '-'*50
#         print 'ALRAM MANAGER START'
#         print '-'*50
#         Manager().main()
#         
#         time.sleep(60)
#         print '-'*50
#         print 'SLEEP 60 SEC'
#     Manager().main()  
#               
# if __name__ == "__main__":
#     vmInfo={}
#     vmInfo['ip'] = '10.10.10.64'
#     vmInfo['username'] = 'administrator@vsphere.local'
#     vmInfo['password'] = 'Kes2719!'
#     VM(vmInfo).main()