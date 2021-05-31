#!/usr/bin/python
#
import atexit
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import time
import datetime
from pyVmomi import vmodl
import sys
import pandas as pd
import MySQLdb
from threading import Thread

df=pd.DataFrame()
start_time = time.time()

def mysqlconnection():
    conn = MySQLdb.connect (host = "10.10.10.64",
                            user = "administrator@vsphere.local",
                            port = 3306,
                            passwd = "Kes2719!",
                            db = "")
    conn.autocommit = True
    return conn

class perfdata():
   '''
       Collect Max, Min, Average of CPU & Memory of VMs in VC. Get vm list from db for which data to be collected
   '''
   row=[]

   def perfcounters(self):
      perfcounter=['cpu.usage.average','mem.usage.average']
      return perfcounter

   def insertdata(self):
      conn = mysqlconnection()
      cursor = conn.cursor()
      cursor.executemany("""INSERT INTO [[table name]] (vcenter_name,cluster_name,host_name,vm_name,cpu_pct_min,ram_pct_min,cpu_pct_max,ram_pct_max,cpu_pct_avg,ram_pct_avg,cpu_pct_samples,ram_pct_samples,stat_dt) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", self.row)
      conn.commit()
      cursor.close()
      conn.close()

   def getdesc(self,df,vc,clsname,hostname,vmname,endTime):
       #print len(df.index)
       df=df['metric'].groupby([df['instance'], df['counter']]).agg(['min','max','mean','count'])
       df['mean']=df['mean'].round(2)
       df.reset_index(inplace='yes')
       #df.to_csv('testfile.csv',sep='\t')
       df=df.pivot_table(index='instance',columns='counter')
       df.reset_index(inplace=True)
       df.fillna(0,inplace=True)
       df.drop_duplicates(inplace=True)
       for i in df.values:
       #sql="insert into (vcenter_name,cluster_name,host_name,vm_name,cpu_pct_min,ram_pct_min,cpu_pct_max,ram_pct_max,cpu_pct_avg,ram_pct_avg,cpu_pct_samples,ram_pct_samples,stat_dt) values('"+vc+"','"+clsname+"','"+hostname+"','"+i[0]+"',"+str(i[1])+","+str(i[2])+","+str(i[3])+","+str(i[4])+","+str(i[5])+","+str(i[6])+","+str(i[7])+","+str(i[8])+",'"+str(endTime)+"')"
          vcenter_name=vc
          cluster_name=clsname
          host_name=hostname
          vm_name=i[0]
          #print vm_name
          cpu_pct_min=str(i[1])
          ram_pct_min=str(i[2])
          cpu_pct_max=str(i[3])
          ram_pct_max=str(i[4])
          cpu_pct_avg=str(i[5])
          ram_pct_avg=str(i[6])
          cpu_pct_samples=str(i[7])
          ram_pct_samples=str(i[8])
          #print "cpu_pct_samples = {} ram_pct_samples= {}".format(i[7],i[8])
          self.row.append((vcenter_name,cluster_name,host_name,vm_name,cpu_pct_min,ram_pct_min,cpu_pct_max,ram_pct_max,cpu_pct_avg,ram_pct_avg,cpu_pct_samples,ram_pct_samples,str(endTime)))

   def getperfdata(self,content,vc,vihost,vmname,hostname,clsname):
       '''
          Get performance data for vm
       '''
       df=pd.DataFrame()
       output=[]
       try:
          perf_dict = {}
          perfManager = content.perfManager
          perfList = content.perfManager.perfCounter
          for counter in perfList: #build the vcenter counters for the objects
              counter_full = "{}.{}.{}".format(counter.groupInfo.key,counter.nameInfo.key,counter.rollupType)
              perf_dict[counter_full] = counter.key
          counter_name = ['cpu.usage.average','mem.usage.average']
          for counter in counter_name:
              counterId = perf_dict[counter]
              metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance="")
              endTime=datetime.datetime.now()
              #startTime = endTime - datetime.timedelta(days=1)
              startTime = endTime - datetime.timedelta(days=1)
              query = vim.PerformanceManager.QuerySpec(entity=vihost,metricId=[metricId],startTime=startTime,endTime=endTime)
              stats=perfManager.QueryPerf(querySpec=[query])
              output=[]
              for val in stats[0].value[0].value:
                  out={}
                  val=float(val/100)
                  #timestamp=stats[0].sampleInfo[0].timestamp
                  #timestamp,tmp=str(timestamp).split("+")
                  out['instance']=vmname
                  out['counter']=counter
                  #out['timestamp']=startTime
                  out['metric']=val
                  output.append(out)
                  #print("{} {} {} {}".format(counter,vmname,timestamp,val))
              df1=pd.DataFrame(output)
              df=df.append(df1)
              #print df
          #pp.pprint(output) 
          print "Calling for vm {}".format(vmname)
          self.getdesc(df,vc,clsname,hostname,vmname,endTime)
       except vmodl.MethodFault as e:
           print("Caught vmodl fault : " + e.msg)
           return 0
       except Exception as e:
           print("Caught exception : " + str(e))
           return 0

def main():
   global df
   user='' ## VC user
   passwd='' ## VC passwd
   port=443
   vc="" ## VC hostname
   try:
       si = SmartConnect(
               host=vc,
               user=user,
               pwd=passwd,
               port=port)
   except:
           print "Failed to connect"
           sys.exit()
   atexit.register(Disconnect, si)
   content = si.RetrieveContent()
   iplist=['10.10.10.64'] ## list of vms
   jobs=[]
   sql="select ip,vmname,hostname,cluster from [[vm table ]] where vc="+vc
   
   cursor=[[execute sql]]
   numrows = int(cursor.rowcount)
   if numrows<1:
       print "Not enough instances"
       sys.exit(0)
   jobs=[]
   for x in range(0,numrows):
       row = cursor.fetchone()
       ip=row[0]
       #print "IP: {}".format(ip)
       vmname=row[1]
       hostname=row[2]
       clsname=row[3]
       perf=perfdata()
       counters=perf.perfcounters()
       search_index=content.searchIndex
       vm=search_index.FindByIp(None, ip, True)
       if vm:
       #ncpu=vm.summary.config.numCpu
          p = Thread(target=perf.getperfdata, args=(content,vc,vm,vmname,hostname,clsname,))
          jobs.append(p)
          p.start()
   for j in jobs:
       j.join()
   print perf.row
#    perf.insertdata()
   #print("""INSERT INTO ecs_reporting.vmware_vm_stats_temp(vcenter_name,cluster_name,host_name,vm_name,cpu_pct_min,ram_pct_min,cpu_pct_max,ram_pct_max,cpu_pct_avg,ram_pct_avg,cpu_pct_samples,ram_pct_samples,stat_dt) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", row) 
   #conn = mysqlconnection()
   #cursor = conn.cursor()
   #cursor.executemany("""INSERT INTO ecs_reporting.vmware_vm_stats_temp(vcenter_name,cluster_name,host_name,vm_name,cpu_pct_min,ram_pct_min,cpu_pct_max,ram_pct_max,cpu_pct_avg,ram_pct_avg,cpu_pct_samples,ram_pct_samples,stat_dt) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", row)
   #conn.commit()
   #cursor.close()
   #conn.close()
   print("--- %s seconds ---" % (time.time() - start_time))

# start
if __name__ == "__main__":
    main()
