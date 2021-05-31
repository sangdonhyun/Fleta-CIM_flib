#!/usr/bin/python
'''
Written by Gaurav Dogra
Github: https://github.com/dograga

Script to extract vm performance data
'''
import atexit
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import time
import datetime
from pyVmomi import vmodl
from threading import Thread
import ssl

class perfdata():
   def perfcounters(self):
      perfcounter=['cpu.usage.average','mem.usage.average','disk.usage.average']
      return perfcounter

   def run(self,content,vm,counter_name):
        print vm.summary.config.uuid
        
        output=[]
        try:
           perf_dict = {}
           perfManager = content.perfManager
           perfList = content.perfManager.perfCounter
           for counter in perfList: #build the vcenter counters for the objects
               counter_full = "{}.{}.{}".format(counter.groupInfo.key,counter.nameInfo.key,counter.rollupType)
               perf_dict[counter_full] = counter.key
           counterId = perf_dict[counter_name]
           metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance="")
           timenow=datetime.datetime.now()
           startTime = timenow - datetime.timedelta(hours=1)
           print startTime
           endTime = timenow
           query = vim.PerformanceManager.QuerySpec(entity=vm,metricId=[metricId],startTime=startTime,endTime=endTime,maxSample=10)
           stats=perfManager.QueryPerf(querySpec=[query])
           count=0
           for val in stats[0].value[0].value:
               perfinfo={}
               val=float(val/100)
               perfinfo['timestamp']=stats[0].sampleInfo[count].timestamp
               perfinfo['hostname']=vm
               perfinfo['value']=val
               output.append(perfinfo)
               count+=1
           for out in output:
               print "Counter: {} Hostname: {}  TimeStame: {} Usage: {}".format (counter_name,out['hostname'],out['timestamp'],out['value'])
        except vmodl.MethodFault as e:
            print("Caught vmodl fault : " + e.msg)
            return 0
        except Exception as e:
            print("Caught exception : " + str(e))
            return 0

def getSi():
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
    

def main():
    vc='10.10.10.64'
    user='administrator@vsphere.local'
    passwd='Kes2719!'
    port=443
    vmip='10.10.10.64'
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
    counters=perf.perfcounters()
    search_index=content.searchIndex
    vm=search_index.FindByIp(None, vmip, True)
    print vm
    ##vm=search_index.FindByDnsName(None, vmdnsname, True)     //vm dnsname is Hostname as reported by vmtool
    
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
#                 print (vmList)
            for vm in vmList:
    
                for counter in counters:
                     p = Thread(target=perf.run,args=(content,vm,counter,))
                     p.start()

# start
if __name__ == "__main__":
    main()

