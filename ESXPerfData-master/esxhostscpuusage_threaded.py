#!/usr/bin/python
"""
Written by Gaurav Dogra
Github: https://github.com/dograga

Script to extract cpu usage of esxhosts on vcenter for last 1 hour with multithreading
"""
import atexit
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import time
import datetime
from pyVmomi import vmodl
from threading import Thread
import ssl
import sys
class perfdata():
   def metricvalue(self,item,depth):
      maxdepth=10
      if hasattr(item, 'childEntity'):
         if depth > maxdepth:
             return 0
         else:
             item = item.childEntity
             item=self.metricvalue(item,depth+1)
      return item

   def run(self,content,vihost):
        print vihost
        output=[]
#        try:
        perf_dict = {}
        perfManager = content.perfManager
        perfList = content.perfManager.perfCounter
        for counter in perfList: #build the vcenter counters for the objects
            counter_full = "{}.{}.{}".format(counter.groupInfo.key,counter.nameInfo.key,counter.rollupType)
            perf_dict[counter_full] = counter.key
#             print counter_full, counter.key
        print perf_dict
        counter_name = 'cpu.usage.average'
        counterId = perf_dict[counter_name]
        
        metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance="")
        metricId = vim.PerformanceManager.MetricId(counterId=6, instance="")
        print 'metricId :',metricId
        """
        counterIDs = [m.counterId for m in
                          perfManager.QueryAvailablePerfMetric(entity=child)]
    
            # Using the IDs form a list of MetricId
            # objects for building the Query Spec
            metricIDs = [vim.PerformanceManager.MetricId(counterId=c,
                                                         instance="*")
                         for c in counterIDs]
    
            # Build the specification to be used
            # for querying the performance manager
            print "metricIDs :",metricIDs
#             sys.exit()
            spec = vim.PerformanceManager.QuerySpec(maxSample=1,
                                                    entity=child,
                                                    metricId=metricIDs)
            # Query the performance manager
            # based on the metrics created above
            result = perfManager.QueryStats(querySpec=[spec])
        (vim.PerformanceManager.MetricId) {
           dynamicType = <unset>,
           dynamicProperty = (vmodl.DynamicProperty) [],
           counterId = 6,
           instance = '*'
        }
        """
        timenow=datetime.datetime.now()
        startTime = timenow - datetime.timedelta(hours=1)
        endTime = timenow
        search_index = content.searchIndex
        
        host = search_index.FindByDnsName(dnsName=vihost, vmSearch=False)
        
        query = vim.PerformanceManager.QuerySpec(entity=host,metricId=[metricId],intervalId=20,startTime=startTime,endTime=endTime)
        stats=perfManager.QueryPerf(querySpec=[query])
        print '-'*50
        print str(stats)
        
        print '-'*50
        count=0
        
       
        
        
        
        for val in stats[0].value[0].value:
            perfinfo={}
            val=float(val/100)
            perfinfo['timestamp']=stats[0].sampleInfo[count].timestamp
            perfinfo['hostname']=vihost
            perfinfo['value']=val
            output.append(perfinfo)
            count+=1
        for out in output:
            print "Hostname: {}  TimeStame: {} Usage: {}".format (out['hostname'],out['timestamp'],out['value'])
#         except vmodl.MethodFault as e:
#            print("Caught vmodl fault : " + e.msg)
#            return 0
#         except Exception as e:
#            print("Caught exception : " + str(e))
#            return 0

def main():
    host='10.10.10.64'
    user='administrator@vsphere.local'
    password='Kes2719!'
    
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
        si = SmartConnect(host=host,
                      user=user,
                      pwd=password,
                      sslContext=context)
    if not si:
        print("Could not connect to the specified host using specified "
              "username and password")
        return -1
    
    atexit.register(Disconnect, si)
   
    content = si.RetrieveContent()
    perf=perfdata()
    perfManager=content.perfManager
    timenow=datetime.datetime.now()
    startTime = timenow - datetime.timedelta(hours=24)
    endTime = timenow
    for child in content.rootFolder.childEntity:
        datacenter=child
        hostfolder= datacenter.hostFolder
        hostlist=perf.metricvalue(hostfolder,0)
        for hosts in hostlist:
#               esxhosts=hosts.host
#               for esx in esxhosts:
#                   summary=esx.summary
#                   esxname=summary.config.name
#                   p = Thread(target=perf.run, args=(content,esxname,))
#                   p.start()
            esxhosts = hosts.host
            counterInfo = {}
            for c in perfManager.perfCounter:
                #print(c)
                #time.sleep(500)
                prefix = c.groupInfo.key
                fullName = c.groupInfo.key + "."+c.nameInfo.key + "." + c.rollupType
                #print(c.groupInfo.key, ' ',c.nameInfo.key,' ',c.rollupType, ' ',c.unitInfo.key)
                counterInfo[fullName] = c.key
                
            for esx in esxhosts:
                summary = esx.summary
                esxname = summary.config.name
                print esxname
                counterIDs = [m.counterId for m in perfManager.QueryAvailablePerfMetric(entity=esx)]
                print counterIDs
                metricIDs = [vim.PerformanceManager.MetricId(counterId=c, instance="*") for c in counterIDs]
#                 print metricIDs
                spec = vim.PerformanceManager.QuerySpec(maxSample=10, entity=esx,intervalId=20,startTime=startTime, endTime=endTime, metricId=metricIDs)
                result = perfManager.QueryStats(querySpec=[spec])
                print('result :',result)
# start
if __name__ == "__main__":
    main()

