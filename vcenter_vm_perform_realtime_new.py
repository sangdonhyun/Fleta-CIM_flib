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
import ConfigParser
import os
import redis_conn
import fletaDbms
import sys



        
            
class Vm():
    def __init__(self,vmInfo):
        self.vmInfo=vmInfo
        self.wbit=False
        self.db=fletaDbms.FletaDb()
        self.r=redis_conn.Redis().r
        
    def perf_keys(self):
#         perfcounter=['cpu.usage.average','cpu.usagemhz.average','mem.usage.average','disk.usage.average']
        perfcounter=[]
        cfg = ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        
        for opt in sorted(set(cfg.options('perform'))):
            perfcounter.append(cfg.get('perform',opt))
        return perfcounter
    
    
   
    
    
    def getSi(self):
        host=self.vmInfo['ip']
        user=self.vmInfo['username']
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
        return si
        
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
        startTime = timenow - datetime.timedelta(seconds=60)
#         print startTime
        endTime = timenow
        return startTime,endTime
    
    
    def AllVm(self,si,content):
        vmAllList=[]
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder'):
                datacenter = child
                vmFolder = datacenter.vmFolder
                vmList = vmFolder.childEntity
#                 print (vmList)
                for vm in vmList:
#                     print (vm)
                    if 'group' not in str(vm): 
                        vmAllList.append(vm)
        return vmAllList
    
    def main(self):
        performList=[]
        si=self.getSi()
        content = si.RetrieveContent()
        perfKyes=self.perf_keys()
        perfManager = content.perfManager
        perfList = content.perfManager.perfCounter
        
        
        
        perf_dict=self.performDic(content)
        
        
        search_index=content.searchIndex
        startTime,endTime = self.getTimes()
        for vm in self.AllVm(si,content):
            uuid= vm.summary.config.uuid
            for perf_key in perfKyes:
                counterId = perf_dict[perf_key]
                metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance="")
                query = vim.PerformanceManager.QuerySpec(maxSample=1,
                                                 entity=vm,
                                                 metricId=[metricId],
                                                 intervalId=20,
                                                 #startTime=self.startTime,endTime=self.endTime,
                                                 format='normal')
                stats=perfManager.QueryPerf(querySpec=[query])
                
                try:
                    for val in stats[0].value[0].value:
                        print uuid,stats[0].sampleInfo[0].timestamp,perf_key,val,float(val)/100
#                         if uuid=='4200454a-71cf-e743-a780-0032abccf0ad':
                        performList.append([uuid,stats[0].sampleInfo[0].timestamp,perf_key,val,float(val)])
                except:
                    pass
        
        return performList
    
    
    def setRedid(self,key,value,check_date):
        rcnt=self.r.hget(key,'avg_count')
        print key
        print 'avg_count :',rcnt,rcnt==None
        if rcnt == None:
            self.r.hset(key,'max',value)
            self.r.hset(key,'sum',value)
            self.r.hset(key,'max_time',check_date)
            self.r.hset(key,'avg_count','1')
        else:
            rmax=self.r.hget(key,'max')
            rmaxtime=self.r.hget(key,'max_time')
            ravg=self.r.hget(key,'sum')
            print ravg,value
            tvalue=float(ravg)+float(value)
            if value > float(rmax):
                rmax=value
                rmaxtime=check_date
            rcnt = float(rcnt)+1
            self.r.hset(key,'max',tvalue)
            self.r.hset(key,'sum',float(ravg)+value)
            self.r.hset(key,'max_time',rmaxtime)
            self.r.hset(key,'avg_count',rcnt)
#             print 'max:',self.r.hget(key,'max')
#             print 'sum:',self.r.hget(key,'sum')
#             print 'max_time:',self.r.hget(key,'max_time')
#             print 'avg_count:',self.r.hget(key,'avg_count')
    
    def run(self):
        plist=self.main()
        #4200454a-71cf-e743-a780-0032abccf0ad W_2016_restapi_68
        
        for p in plist:
#             print p
            uuid=p[0]
            check_date=p[1].strftime('%Y-%m-%d %H:%M:%S')
            arg=p[2].split('.')
            key='%s::%s::%s_%s'%(check_date,uuid,arg[0],arg[1])
            value=int(round(p[-1]))
            if p[2] =='cpu.usage.average':
                value=int(round(float(value/100)))
                key=key+'::%'
            filed=arg[2]
            print key,filed,value
            self.r.hset(key,filed,value)
            minstr=p[1].strftime('%Y-%m-%d %H:%M')
            min10str=p[1].strftime('%M')
            if int(int(min10str))%10 != 0:
                min10str=p[1].strftime('%M')
                if len(p[1].strftime('%M'))==1:
                    min=10
                else:
                    min=min10str[0]+'0'
                tminstr = p[1].strftime('%Y-%m-%d %H:')+min
            else:
                tminstr = minstr
            print tminstr
                
                
            minkey='{}::{}::{}_{}'.format(tminstr,uuid,arg[0],arg[1])
            self.setRedid(minkey,value,check_date)
        
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
        print 'v-center vm perform'
        hostList=self.getHost()
        for host in hostList:
#             print host
            Vm(host).run()

if __name__ == "__main__":
#     while True:
#         Manager().main()
#         time.sleep(3)
    Manager().main()



