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
nextDateHour=''

class perfdata():
    def __init__(self):
        self.db=fletaDbms.FletaDb()
        self.preDateHour=''
        self.dbBit=True
        
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
    def __init__(self):
        self.db=fletaDbms.FletaDb()
        self.preDateHour=''
        self.wbit=False
        self.nextDateHour=''
        self.r = redis_conn.Redis().conn()
        
    def perf_keys(self):
        perfcounter=['cpu.usage.average','cpu.usagemhz.average','mem.usage.average','disk.usage.average']
        perfcounter=[]
        cfg = ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        
        for opt in sorted(set(cfg.options('perform'))):
            perfcounter.append(cfg.get('perform',opt))
        return perfcounter
    
    
    def run(self,content,vm,perf_dict,startTime,endTime):
        self.content=content
        self.vm=vm
        self.perf_dict=perf_dict
        self.startTime=startTime
        self.endTime=endTime
        
        
        
        try:
            name=self.vm.summary.config.name
        except:
            name='n/a'
        perfKyes=self.perf_keys()
        perfManager = self.content.perfManager
        perfList = self.content.perfManager.perfCounter
#         print 'perfList :',perfList
        print '-'*50
        
        redisList=[]
        avgList=[]
        """
        name=cpu.usage.average
        key=564d2e7e-393a-b454-d7bd-a4688998dc92::2019-05-10 14:57:00+00:00
        value=0.0
        """
        self.wbit=False
        statisticDateHour=''
        
        datetime=''
        
        for perf_key in perfKyes:
            
            counterId = self.perf_dict[perf_key]
            metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance="")
            query = vim.PerformanceManager.QuerySpec(intervalId=20,entity=self.vm,metricId=[metricId],startTime=self.startTime,endTime=self.endTime,maxSample=5)
            query = vim.PerformanceManager.QuerySpec(maxSample=2,
                                             entity=self.vm,
                                             metricId=[metricId],
                                             intervalId=20,
                                             #startTime=self.startTime,endTime=self.endTime,
                                             format='normal')
    
            stats=perfManager.QueryPerf(querySpec=[query])
#             try:
            count=0
            
            
            try:
                print 'value :',stats[0].value[0].value
            except:
                break
            
            
            for val in stats[0].value[0].value:
#                     print stats[0].sampleInfo[count]
                redisInfo={}
                avgInfo={}
                print self.uuid
                print self.uuid,stats[0].sampleInfo[count].timestamp,perf_key,val,float(val/100)
                count = count +1
                try:
                    timestr= stats[0].sampleInfo[count].timestamp
                except:
                    break
                    
                
                datetime= timestr.strftime('%Y-%m-%d %H:%M:%S')
                statisticDateHour=timestr.strftime('%Y-%m-%d %H')
                
                
                avg1,avg2,avg3=perf_key.split('.')
                print perf_key
                
                keys='%s::%s::%s::%s'%(datetime,self.uuid,avg1,avg2)
                print keys
                redisInfo['redis_key']=keys
                redisInfo['redis_filed']=avg3
                redisInfo['redis_value']=float(val/100)
                redisList.append(redisInfo)
                
                avgkey='%s::%s::%s::%s'%(statisticDateHour,self.uuid,avg1,avg2)
                r=redis_conn.Redis().r
    
                rmax=r.hget(avgkey,'max')
                rmaxtime=r.hget(avgkey,'max_time')
                ravg=r.hget(avgkey,'avg')
                print 'key :',avgkey
                rcnt=r.hget(avgkey,'avg_count')
            
                print '*'*50
                print avgkey
                
                print rcnt,rcnt==None
                
                ins_date=timestr.strftime('%Y-%m-%d')
                
                query_string="select count(*) from monitor.perform_stg_avg  where ins_date='{}' and ctrl_unum ='{}' and check_date ='{}'".format(ins_date,self.uuid,statisticDateHour)
                cnt=self.db.getRaw(query_string)[0][0]
                print query_string
                print cnt
                if int(cnt) == 0:
                    avgDic={}
                    avgDic={}
                    avgDic['ins_date']=ins_date
                    avgDic['check_date']=statisticDateHour
                    avgDic['ctrl_unum']=self.uuid
                    avgDic['flag_nm']='{}_{}'.format(avg1,avg2)
                    avgDic['cols_nm']=avg3
                    avgDic['cols_value_max']=rmax
                    avgDic['cols_max_date']=rmaxtime
                    avgDic['cols_value_avg']=float(float(ravg)/float(rcnt))
                    print '='*50
                    print float(float(ravg)/float(rcnt))
                    print avgDic
                    print '='*50
                    self.db.dicInsert(avgDic, 'monitor.perform_stg_avg')
                    
                    
                
                if rcnt ==None:
                    print '#'*50
#                     print rmax,rmax,type(rmax),rmax==None,rmaxtime,ravg,rcnt,redisInfo['redis_value'] > rmax
                    print avgkey
                    print '#'*50
                    try:
                        r.hset(avgkey,'max',redisInfo['redis_value'])
                        r.hset(avgkey,'avg',redisInfo['redis_value'])
                        r.hset(avgkey,'max_time',datetime)
                        r.hset(avgkey,'avg_count','1')
                    except:
                        pass
                
                    rcnt=r.hget(avgkey,'avg_count')
                    print rcnt,rcnt==None
                    
                    
                else:
                    print '+'*50
                    if float(redisInfo['redis_value']) > rmax:
                
                        r.hset(avgkey,'max',redisInfo['redis_value'])
                        r.hset(avgkey,'max_time',datetime)
            
                    ravg = str(float(redisInfo['redis_value'])+float(ravg))
            
                    r.hset(avgkey,'avg',ravg)
                    r.hset(avgkey,'avg_count',int(rcnt)+1)
                
                    print "avg keys :",avgkey
                    print 'avg_count',int(rcnt) +1
                    
                    
                 
                """ 
                avg_max_field='max'
                avg_max_value='99'
                avg_field_01='max_time'
                avg_value_01='2019-05-04 19:22:22'
                avg_avg_field='average'
                avg_avg_value='99'
                """
                    
                
#             except:
#                 pass
            redis_conn.Redis().run(redisList)
            print datetime
            if datetime != '':
                redisInfo={}
                
                redisInfo['last_key']='vmwear_latest_time_{}'.format(self.uuid)
                redisInfo['last_val']=datetime
                print redisInfo
                redis_conn.Redis().setdic(redisInfo)
        if statisticDateHour != '':
            return statisticDateHour
           
        
        
            
class Vm():
    def __init__(self,vmInfo):
        self.vmInfo=vmInfo
        self.wbit=False
        self.db=fletaDbms.FletaDb()
        self.r = redis_conn.Redis().conn()
        
    def perf_keys(self):
#         perfcounter=['cpu.usage.average','cpu.usagemhz.average','mem.usage.average','disk.usage.average']
        perfcounter=[]
        cfg = ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        
        for opt in sorted(set(cfg.options('perform'))):
            perfcounter.append(cfg.get('perform',opt))
        return perfcounter
    
    
    def run(self,content,vm,perf_dict,startTime,endTime,uuid,hbit=False):
        self.content=content
        self.vm=vm
        self.perf_dict=perf_dict
        self.startTime=startTime
        self.endTime=endTime
        
        
        
        try:
            name=self.vm.summary.config.name
        except:
            name='n/a'
        perfKyes=self.perf_keys()
        perfManager = self.content.perfManager
        perfList = self.content.perfManager.perfCounter
#         print 'perfList :',perfList
        print '-'*50
        
        redisList=[]
        avgList=[]
        """
        name=cpu.usage.average
        key=564d2e7e-393a-b454-d7bd-a4688998dc92::2019-05-10 14:57:00+00:00
        value=0.0
        """
        self.wbit=False
        statisticDateHour=''
        
        datetime=''
        
        
        for perf_key in perfKyes:
            
            counterId = self.perf_dict[perf_key]
            metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance="")
            query = vim.PerformanceManager.QuerySpec(intervalId=20,entity=self.vm,metricId=[metricId],startTime=self.startTime,endTime=self.endTime,maxSample=5)
            query = vim.PerformanceManager.QuerySpec(maxSample=2,
                                             entity=self.vm,
                                             metricId=[metricId],
                                             intervalId=20,
                                             #startTime=self.startTime,endTime=self.endTime,
                                             format='normal')
    
            stats=perfManager.QueryPerf(querySpec=[query])
#             try:
            count=0
            
            
            try:
                print 'value :',stats[0].value[0].value
            except:
                break
            
            
            for val in stats[0].value[0].value:
#                     print stats[0].sampleInfo[count]
                redisInfo={}
                avgInfo={}
                self.uuid=uuid
                print self.uuid,stats[0].sampleInfo[count].timestamp,perf_key,val,float(val/100)
                count = count +1
                try:
                    timestr= stats[0].sampleInfo[count].timestamp
                except:
                    break
                    
                
                datetime= timestr.strftime('%Y-%m-%d %H:%M:%S')
                statisticDateHour=timestr.strftime('%Y-%m-%d %H')
                
                
                avg1,avg2,avg3=perf_key.split('.')
                print perf_key
                
                keys='%s::%s::%s::%s'%(datetime,self.uuid,avg1,avg2)
                print keys
                redisInfo['redis_key']=keys
                redisInfo['redis_filed']=avg3
                redisInfo['redis_value']=float(val/100)
                redisList.append(redisInfo)
                
                avgkey='%s::%s::%s::%s'%(statisticDateHour,self.uuid,avg1,avg2)


                rmax=self.r.hget(avgkey,'max')
                rmaxtime=self.r.hget(avgkey,'max_time')
                ravg=self.r.hget(avgkey,'avg')
                print 'key :',avgkey
                rcnt=self.r.hget(avgkey,'avg_count')
            
                print '*'*50
                print avgkey
                
                print rcnt,rcnt==None
                
                ins_date=timestr.strftime('%Y-%m-%d')
                
                    
                    
                
                if rcnt ==None:
                    print '#'*50
#                     print rmax,rmax,type(rmax),rmax==None,rmaxtime,ravg,rcnt,redisInfo['redis_value'] > rmax
                    print avgkey
                    print '#'*50
                    try:
                        self.r.hset(avgkey,'max',redisInfo['redis_value'])
                        self.r.hset(avgkey,'avg',redisInfo['redis_value'])
                        self.r.hset(avgkey,'max_time',datetime)
                        self.r.hset(avgkey,'avg_count','1')
                    except:
                        pass
                
                    rcnt=self.r.hget(avgkey,'avg_count')
                    print rcnt,rcnt==None
                    
                    
                else:
                    print '+'*50
                    if float(redisInfo['redis_value']) > rmax:
                
                        self.r.hset(avgkey,'max',redisInfo['redis_value'])
                        self.r.hset(avgkey,'max_time',datetime)
            
                    ravg = str(float(redisInfo['redis_value'])+float(ravg))
            
                    self.r.hset(avgkey,'avg',ravg)
                    self.r.hset(avgkey,'avg_count',int(rcnt)+1)
                
                    print "avg keys :",avgkey
                    print 'avg_count',int(rcnt) +1
                    
                    
                
                query_string="select count(*) from monitor.perform_stg_avg  where ins_date='{}' and ctrl_unum ='{}' and check_date ='{}'".format(ins_date,self.uuid,statisticDateHour)
                try:
                    cnt=self.db.getRaw(query_string)[0][0]
                except:
                    cnt = 0
                print query_string
                print cnt
                
                if rcnt  != None:
#                 if int(cnt) == 0:
                    
                    print 'max:',rmax
                    print 'maxtime:',rmaxtime
                    print 'avg sum :',ravg
                    print 'avg_cnt :',rcnt
                    
                    avgDic={}
                    try:
                        avgDic={}
                        avgDic['ins_date']=ins_date
                        avgDic['check_date']=statisticDateHour
                        avgDic['ctrl_unum']=self.uuid
                        avgDic['flag_nm']='{}_{}'.format(avg1,avg2)
                        avgDic['cols_nm']=avg3
                        avgDic['cols_value_max']=rmax
                        avgDic['cols_max_date']=rmaxtime
                        avgDic['cols_value_avg']=float(float(ravg)/float(rcnt))
                        print '='*50
                        print float(float(ravg)/float(rcnt))
                        print avgDic
                        print '='*50
                        self.db.dicInsert(avgDic, 'monitor.perform_stg_avg')
                    except :
                        pass
                 
                """ 
                avg_max_field='max'
                avg_max_value='99'
                avg_field_01='max_time'
                avg_value_01='2019-05-04 19:22:22'
                avg_avg_field='average'
                avg_avg_value='99'
                """
                    
                
#             except:
#                 pass
            redis_conn.Redis().run(redisList)
            print datetime
            if datetime != '':
                redisInfo={}
                
                redisInfo['last_key']='vmwear_latest_time_{}'.format(self.uuid)
                redisInfo['last_val']=datetime
                print redisInfo
                redis_conn.Redis().setdic(redisInfo)
        if statisticDateHour != '':
            return statisticDateHour
           
    
    
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
                          port=int(port),
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
                    print vm.summary
                    try:
                        uuid=vm.summary.config.uuid
                    except:
                        uuid=None
                    if uuid != None:
                        print uuid
                        self.run(content,vm,perf_dict,startTime,endTime,uuid)
#                         PerformBatch().run(content,vm,perf_dict,startTime,endTime)
                        
#                     p = Thread(target=PerformBatch.run,args=(content,vm,perf_dict,startTime,endTime))
#                     p.start()
                    """
                    for counter in counters:
                         p = Thread(target=PerformBatch.run,args=(content,vm,counter,))
                         p.start()
                    """
        

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
            print host
            Vm(host).main()

if __name__ == "__main__":
    while True:
        Manager().main()
        time.sleep(5)



