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
import configparser
import os

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


class PerformBatch():
        
    def perf_keys(self):
        perfcounter=['cpu.usage.average','cpu.usagemhz.average','mem.usage.average','disk.usage.average']
        
        return perfcounter
    
    
    def run(self,content,vm,perf_dict,startTime,endTime):
        self.content=content
        self.vm=vm
        self.perf_dict=perf_dict
        self.startTime=startTime
        self.endTime=endTime
        try:
            self.uuid=vm.summary.config.uuid
        except:
            pass
        
#         name=self.vm.summary.config.name
        perfKyes=self.perf_keys()
        perfManager = self.content.perfManager
        perfList = self.content.perfManager.perfCounter
#         print 'perfList :',perfList
        print '-'*50
        
        
        for perf_key in perfKyes:
            counterId = self.perf_dict[perf_key]
            metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance="")
            query = vim.PerformanceManager.QuerySpec(intervalId=20,entity=self.vm,metricId=[metricId],startTime=self.startTime,endTime=self.endTime,maxSample=5)
            query = vim.PerformanceManager.QuerySpec(maxSample=30,
                                             entity=self.vm,
                                             metricId=[metricId],
                                             intervalId=60*60*24,
                                             startTime=self.startTime,endTime=self.endTime,
                                             format='normal')
    
            stats=perfManager.QueryPerf(querySpec=[query])
            try:
                count=0
                for val in stats[0].value[0].value:
#                     print stats[0].sampleInfo[count]
                    print self.uuid,stats[0].sampleInfo[count].timestamp,perf_key,val,float(val/100)
                    count = count +1
                    
            except:
                pass
class Vm():
    def __init__(self,vmInfo):
        self.vmInfo=vmInfo
           
    def getSi(self):
        host='10.10.10.64'
        host=self.vmInfo['ip']
        user='administrator@vsphere.local'
        user=self.vmInfo['username']
        password='Kes2719!'
        password=self.vmInfo['password']
        
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
        
    def performDic(self,content):
        perf_dict = {}
        perfManager = content.perfManager
        perfList = content.perfManager.perfCounter
        for counter in perfList: #build the vcenter counters for the objects
            counter_full = "{}.{}.{}".format(counter.groupInfo.key,counter.nameInfo.key,counter.rollupType)
            perf_dict[counter_full] = counter.key
        return perf_dict
    
    
    def getTimes(self):
        timenow=datetime.datetime.now()
        startTime = timenow - datetime.timedelta(days=30)
        print startTime
        endTime = timenow
        return startTime,endTime
    
    def main(self):
        
        host=self.vmInfo['ip']
        user=self.vmInfo['username']
        password=self.vmInfo['password']
        port = self.vmInfo['port']
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
            si = SmartConnect(host=host,
                          user=user,
                          pwd=password,
                          port = int(port),
                          sslContext=context)
        if not si:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1
        
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        perf=perfdata()
        perf_dict=self.performDic(content)
        counters=perf.perfcounters()
        search_index=content.searchIndex
        startTime,endTime = self.getTimes()
        
        ##vm=search_index.FindByDnsName(None, vmdnsname, True)     //vm dnsname is Hostname as reported by vmtool
        
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder'):
                datacenter = child
                vmFolder = datacenter.vmFolder
                vmList = vmFolder.childEntity
#                 print (vmList)
                for vm in vmList:
                    PerformBatch().run(content,vm,perf_dict,startTime,endTime)
#                     p = Thread(target=PerformBatch.run,args=(content,vm,perf_dict,startTime,endTime))
#                     p.start()
                    """
                    for counter in counters:
                         p = Thread(target=PerformBatch.run,args=(content,vm,counter,))
                         p.start()
                    """
# start

class Manager():
    def __init__(self):
        self.cfg = self.getCFg()
    
    
    def getCFg(self):
        cfg = configparser.RawConfigParser()
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
        print 'v-center vm perform'
        hostList=self.getHost()
        for host in hostList:
            print host
            Vm(host).main()

if __name__ == "__main__":
    Manager().main()



