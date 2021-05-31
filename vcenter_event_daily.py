'''
Created on 2019. 5. 8.

@author: Administrator
'''
from __future__ import print_function
import os
import sys
import ConfigParser
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import datetime
import time
import argparse
import atexit
import getpass
import ssl
import time
import socketClient
context = None
# from tools import alarm
# from tools import cli
from datetime import datetime, timedelta
import fletaSnmp
import sys

class Event():
    def __init__(self,vcInfo):
        
        self.vcName=vcInfo['name']
        self.host=vcInfo['ip']
        self.user=vcInfo['username']
        self.password=vcInfo['password']
        self.port = vcInfo['port']
        self.si=self.baseConfig()
        self.dfile=os.path.join('config','%s_dTime.txt'%self.vcName)
        self.now=datetime.now()

    def baseConfig(self):
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
            si = SmartConnect(host=self.host,
                          user=self.user,
                          pwd=self.password,
                          port=self.port,
                          sslContext=context)

            return si
        
    def getDate(self):
        
        if os.path.isfile(self.dfile): 
            with open(self.dfile) as f:
                timestr=f.read()
            dateset=datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')
        else:
            dateset=self.now - timedelta(days=1)
            
        return dateset
    
    def getEvent(self,startDate,endDate):
        events = []
        time_filter = vim.event.EventFilterSpec.ByTime()
        atexit.register(Disconnect, self.si)
        content = self.si.RetrieveContent()
        time_filter = vim.event.EventFilterSpec.ByTime()
        
        dateset=self.getDate()
        
        time_filter.beginTime = dateset
        time_filter.endTime = self.now

        time_filter.beginTime = startDate
        time_filter.endTime   = endDate
        event_type_list = []
        filter_spec = vim.event.EventFilterSpec(eventTypeId=event_type_list, time=time_filter)
        

        eventManager = self.si.content.eventManager
        print (filter_spec)
        event_collector = eventManager.CreateCollectorForEvents(filter_spec)

        print (event_collector)
        page_size = 1000 # The default and also the max vcenter_evet number per page till vSphere v6.5, you can change it to a smaller value by SetCollectorPageSize().
        

        while True:
            # If there's a huge number of events in the expected time range, this while loop will take a while.
            events_in_page = event_collector.ReadNextEvents(page_size)
            num_event_in_page = len(events_in_page)
            if num_event_in_page == 0:
                break   
            events.extend(events_in_page) # or do other things on the collected events
            # Please note that the events collected are not ordered by the vcenter_evet creation time, you might find the first vcenter_evet in the third page for example.
        
        print(
            "Got totally {} events in the given time range from {} to {}.".format(
                len(events), time_filter.beginTime, time_filter.endTime
            )
        )


        return events
# 
# print (ev.fullFormattedMessage)
# print (ev.chainId)
# print (ev.chreateTime)

    def setdTime(self):
        with open(self.dfile,'w') as f:
            f.write(self.now.strftime('%Y-%m-%d %H:%M:%S'))
    
    def getLastkey(self):
        keyFile=os.path.join('config','%s_key.txt')
        if os.path.isfile(keyFile):
            with open(keyFile) as f:
                key=f.read()
        else:
            key=''
        return key
    
    def setLastkey(self,key):
        keyFile=os.path.join('config','%s_key.txt'%self.vcName)
        with open(keyFile,'w') as fw:
            fw.write(key)
        
            
    def main(self):
        
        endDate=self.now
        startDate=self.getDate()
        print( startDate,endDate),( type(startDate),type(endDate))
        
        
            
        lastKey=self.getLastkey()
        events=self.getEvent(startDate, endDate)
        tday=startDate.strftime('%Y%m%d')
        key=''
        
        searchIndex = self.si.RetrieveContent().searchIndex
        vms = searchIndex.FindAllByIp(ip=self.host, vmSearch=True)
        print ('vms :',vms)
        
        with open('event_d_%s.txt'%tday,'w') as f:


            for event in events:
                typeSet= str(type(event))
                eventType=typeSet.split('.')[-1]
                eventType=eventType.replace("'>",'')
                print (eventType)
                print (event)
                key=str(event.key)
                if eventType not in  ['UserLoginSessionEvent','UserLogoutSessionEvent']:
                    if eventType == 'TaskEvent':
                        desc='%s '
                    print ('-'*30)
                    
                    print (event.chainId)
                    print (event.userName)
                    
                    try:
                        print (event.createdTime.strftime('%Y-%m-%d %H:%M:%S'))
                    except:
                        print ('createtime error')
                    event.fullFormattedMessage
                    errDic={}
                    errDic['serial']=self.host
                    errDic['event_date']=event.createdTime.strftime('%Y-%m-%d %H:%M:%S')
                    errDic['event_code']=str(event.key)
                    errDic['severity']='Red'
                    
                    errDic['vendor']='VMware'
                    errDic['device_type']='VCT'
                    errDic['method'] = 'snmp'
                    errDic['etc'] =eventType
                    
#                     if str(lastKey) != str(key):
                    try:
                        print (str(event.fullFormattedMessage))
                        errDic['desc']=str(event.fullFormattedMessage)
                        fletaSnmp.Load().errSnmpTrapSendV2(errDic)
                        print ('snmp put')
                        print (errDic)
                    except:
                        pass

        print ('END')
        self.setdTime()
        print ('key :',key)
        self.setLastkey(key)


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
        print (sys.version)
        print ('v-center Event')
        
        vcList=self.getHost()
        for vc in vcList:
            print (vc)

            Event(vc).main()

    


if __name__=='__main__':
    while True:
        Manager().main()
        print ('wait next 60 sec')
        time.sleep(60)
#     Manager().main()