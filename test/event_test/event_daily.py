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
from tools import alarm
from tools import cli
from datetime import datetime, timedelta

class Event():
    def __init__(self):
        

        self.host='10.10.10.64'
        self.user='administrator@vsphere.local'
        self.password='Kes2719!'
        self.si=self.baseConfig()

    def baseConfig(self):
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
            si = SmartConnect(host=self.host,
                          user=self.user,
                          pwd=self.password,
                          sslContext=context)

            return si
    def getEvent(self,startDate,endDate):
        events = []
        time_filter = vim.event.EventFilterSpec.ByTime()
        atexit.register(Disconnect, self.si)
        content = self.si.RetrieveContent()
        time_filter = vim.event.EventFilterSpec.ByTime()
#             now = datetime.now()
#             time_filter.beginTime = now - timedelta(days=1)
#             time_filter.endTime = now

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


    def test(self):
        endDate=datetime.now()
        startDate=endDate - timedelta(days=1)
        print( startDate,endDate),( type(startDate),type(endDate))
        for i in range(30):
            em = self.si.content.eventManager
            efspec = vim.event.EventFilterSpec()
        
            efspec.category = ["error"]
        
            efespec = vim.event.EventFilterSpec.ByEntity()
            efespec.entity = self.si.content.rootFolder
            efespec.recursion = vim.event.EventFilterSpec.RecursionOption.all
            efspec.entity = efespec
        
            eftspec = vim.event.EventFilterSpec.ByTime()
            now = datetime(2019, 6, 4)
            eftspec.beginTime = now - timedelta(days=1)
            eftspec.endTime = now
            efspec.time = eftspec
#             print (efspec)
        
    #     now = datetime.now()
    #             time_filter.beginTime = now - timedelta(days=1)
    #             time_filter.endTime = now
        
            ehc = em.CreateCollectorForEvents(efspec)
            ehc.SetCollectorPageSize(1000)
            events = ehc.latestPage
            total = len(events)
            print ('TOTAL :',total)
            with open('event_f_%s.txt'%startDate.strftime('%Y%m%d'),'w') as fw:
                while(len(events) > 0):
                    
                    for i, e in enumerate(events):
                        print ("%d -> %s::%s" % (i, e.createdTime, e.fullFormattedMessage))
                        print (e)
                        fw.write(str(e))
                    ehc.ResetCollector()
                    events = ehc.ReadPreviousEvents(1000)
                    total += len(events)
                    if total > 1000:
                        break
                    
                    
            endDate=endDate - timedelta(days=1)
            startDate=startDate - timedelta(days=1)
#     
    
        return 0

    def OneDay(self):
        endDate=datetime(2019, 5, 10)
        self.td=endDate.strftime('%Y%m%d')
        startDate=endDate - timedelta(days=1)
        print( startDate,endDate),( type(startDate),type(endDate))
        
        em = self.si.content.eventManager
        efspec = vim.event.EventFilterSpec()
    
        efspec.category = ["error"]
    
        efespec = vim.event.EventFilterSpec.ByEntity()
        efespec.entity = self.si.content.rootFolder
        efespec.recursion = vim.event.EventFilterSpec.RecursionOption.all
        efspec.entity = efespec
    
        eftspec = vim.event.EventFilterSpec.ByTime()
        now = datetime(2019, 5, 10)
        eftspec.beginTime = now - timedelta(days=1)
        eftspec.endTime = now
        efspec.time = eftspec
        ehc = em.CreateCollectorForEvents(efspec)
        ehc.SetCollectorPageSize(1000)
        events = ehc.latestPage
        total = len(events)
        print ('CNT :%s',total)
        while(len(events) > 0):
            
            for i, e in enumerate(events):
                print ("%d -> %s::%s" % (i, e.createdTime, e.fullFormattedMessage))
                print (e)
                self.fwrite(str(e))
            ehc.ResetCollector()
            events = ehc.ReadPreviousEvents(1000)
            total += len(events)
            if total > 1000:
                break
            
                
    def fwrite(self,msg,wbit='a'): 
          
        with open('event_f_%s.txt'%self.td,'w') as fw:
            fw.wraite(msg+'\n')

    def main(self):
        
        endDate=datetime.now()
        startDate=endDate - timedelta(days=1)
        print( startDate,endDate),( type(startDate),type(endDate))
        
        for i in range(3):
            
            
            events=self.getEvent(startDate, endDate)
            tday=startDate.strftime('%Y%m%d')
            with open('event_e_%s.txt'%tday,'w') as f:
                
                for event in events:
                    print (type(event))
                    print (event)
                    f.write('-'*50+'\n')
                    f.write(str(event))
            startDate=startDate - timedelta(days=1)
            endDate=endDate - timedelta(days=1)


if __name__=='__main__':
    Event().OneDay()