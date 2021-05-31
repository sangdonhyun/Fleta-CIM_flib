#!/usr/bin/env python
"""
 Written by Lance Hasson
 Github: https://github.com/JLHasson

 Script to report all available realtime performance metrics from a
 virtual machine. Based on a Java example available in the VIM API 6.0
 documentationavailable online at:
 https://pubs.vmware.com/vsphere-60/index.jsp?topic=%2Fcom.vmware.wssdk.pg.
 doc%2FPG_Performance.18.4.html&path=7_1_0_1_15_2_4

 Requirements:
     VM tools must be installed on all virtual machines.
"""

from pyVmomi import vim
from pyVim.connect import SmartConnectNoSSL, Disconnect
import atexit
import sys
import datetime



class vm_Perform():
    def __init__(self,vmInfo):
        
        
        self.host = vmInfo['ip']
        self.user = vmInfo['username']
        self.passwd=vmInfo['password']
        self.port = vmInfo['port']
        self.si = self.get_si()
        self.content = self.si.RetrieveContent()
        self.st,self.et= self.get_datetime()
    
    def get_datetime(self,time_lap=20):
        vchtime=self.si.CurrentTime()
        endTime = vchtime - datetime.timedelta(seconds=60)
        startTime = endTime - datetime.timedelta(seconds=time_lap)

        
        return startTime,endTime
    
    def get_si(self):
                # Connect to the host without SSL signing
        try:
            si = SmartConnectNoSSL(
                host=self.host,
                user=self.user,
                pwd=self.passwd,
                port=int(self.port))
            atexit.register(Disconnect, si)
        except IOError as e:
            pass
    
        if not si:
            raise SystemExit("Unable to connect to host with supplied info.")
        return si
    
    
    def get_counters(self):
        counterInfo = {}
        for c in self.perfManager.perfCounter:
            fullName = c.groupInfo.key + "." + c.nameInfo.key + "." + c.rollupType
            counterInfo[fullName] = c.key
        return counterInfo
    
    def get_vmList(self):
        
        # create a mapping from performance stats to their counterIDs
        # counterInfo: [performance stat => counterId]
        # performance stat example: cpu.usagemhz.LATEST
        # counterId example: 6
        
    
        # create a list of vim.VirtualMachine objects so
        # that we can query them for statistics
        container = self.content.rootFolder
        viewType = [vim.VirtualMachine]
        recursive = True
    
        containerView = self.content.viewManager.CreateContainerView(container,
                                                                viewType,
                                                                recursive)
        vms = containerView.view
        
        return vms


    def get_vmPerform(self,vm,interval,metricIDs,countInfo):
        
        spec = vim.PerformanceManager.QuerySpec(maxSample=1,
                                                entity=vm,
                                                intervalId=interval,
#                                                 startTime=self.st,
#                                                 endTime = self.et,
                                                metricId=metricIDs)
        
        # Query the performance manager
        # based on the metrics created above
        result = self.perfManager.QueryStats(querySpec=[spec])

        # Loop through the results and print the output
        output = ""
#         print result
        
        for r in result:
#             print r
            
            
            for val in result[0].value:
                
                
                counterinfo_k_to_v = countInfo.keys()[countInfo.values().index(val.id.counterId)]
                
                print counterinfo_k_to_v
#                 print val
                valList=[]
                for val in val.value:
                    valList.append(val)
                
                print 'value langs  :',len(valList)    
                print 'lasttest val :',valList[0]
                print 'max      val :',max(valList)
                print 'avg      val :',round(sum(valList,0.0)/len(valList),2)
#                 if val.id.instance == '':
#                         output += "%s: %s\n" % (
#                         counterinfo_k_to_v, str(val.value[0]))
#                 else:
#                     output += "%s (%s): %s\n" % (
#                         counterinfo_k_to_v, val.id.instance, str(val.value[0]))

        print(output)

    
    def vmGuest(self):
        output = ""
        print 'CURRENT TIME :',self.si.CurrentTime()
        
        
        self.perfManager = self.content.perfManager
    
        countInfo=self.get_counters()
        # 20 sec 600 sec 600*24 sec
        interval=20
        vms=self.get_vmList()    
        # Loop through all the VMs
        for vm in vms:
            output += "name:        " + vm.summary.config.name + "\n"
            output += "uuid:        " + vm.summary.config.uuid + "\n"
            print dir(vm.summary)
            powerstatus= vm.summary.runtime.powerState
            if powerstatus != 'poweredOff' :
                print 'POWER :',powerstatus
                # Get all available metric IDs for this VM
                counterIDs = [m.counterId for m in
                              self.perfManager.QueryAvailablePerfMetric(entity=vm)]
                # Using the IDs form a list of MetricId
                # objects for building the Query Spec
                counterIDs=[2,24,125,205]
                metricIDs = [vim.PerformanceManager.MetricId(counterId=c,
                                                             instance="*")
                             for c in counterIDs]
                
                print output
                print 'realtime'
                print '-'*30
                self.st,self.et=self.get_datetime(60)
                print self.st,self.et
                self.get_vmPerform(vm, 20 , metricIDs, countInfo)
#                 print '10min avg'
#                 print '-'*30
#                 self.get_vmPerform(vm, 300, metricIDs, countInfo)
                
#                 print '1 hour avg'
#                 print '-'*30
#                 self.get_vmPerform(vm, 600*6, metricIDs, countInfo)
#                 print '24 hour avg'
#                 print '-'*30
#                 self.get_vmPerform(vm, 600*6*24, metricIDs, countInfo)
                # Build the specification to be used
                # for querying the performance manager
            else:
                powerstatus
                
    def GetVMHosts(self):
        print("Getting all ESX hosts ...")
        host_view = self.content.viewManager.CreateContainerView(self.content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj
    
    def host_perform(self):
        
        hosts = self.GetVMHosts()
        """
        Obtains the current CPU usage of the Host
    
        :param host_moref: Managed Object Reference for the ESXi Host
        """
        print hosts
        for host in hosts:
            print host.summary
            print 'hostname',host.name
            print '-'*40
            host_cpu = host.summary.quickStats.overallCpuUsage
            host_total_cpu = host.summary.hardware.cpuMhz * host.summary.hardware.numCpuCores
            final_output = (host_cpu / host_total_cpu) * 100
            print("CPU:", round(((host.hardware.cpuInfo.hz/1e+9)*host.hardware.cpuInfo.numCpuCores),0),"GHz")
            print 'HOST CPU       : %s'%int(host_cpu)
            print 'HOST CPU TOTAL : %s'%int(host_total_cpu)
            final_output = round((float(host_cpu)/float(host_total_cpu))*100,2)
            print 'CPU USAGE      : %s'%final_output
            
            
             
            
            """
            Obtains the current Memory usage of the Host
        
            :param host_moref: Managed Object Reference for the ESXi Host
            """
    
            host_memory = host.summary.quickStats.overallMemoryUsage
            host_total_memory = host.summary.hardware.memorySize / 1024 /1024
            final_output = (host_memory / host_total_memory) * 100
            print  "MEM :%s"%host.hardware.memorySize
            print 'HOST MEM       : %s'%int(host_memory)
            print 'HOST MEM TOTAL : %s'%int(host_total_memory)
            final_output = round((float(host_memory)/float(host_total_memory))*100,2)
            print 'MEM USAGE      : %s'%final_output
         
        """
            
                                                           
        for host in hosts:
            # Print the hosts cpu details
            print(dir(host))
            self.fwrite(str(host.summary))
            # convert CPU to total hz to ghz times numCpuCores
#             print("CPU:", round(((host.hardware.cpuInfo.hz/1e+9)*host.hardware.cpuInfo.numCpuCores),0),"GHz")
            #covert the raw bytes to readable size via convertMemory
#             print("Memory:", convertMemory(host.hardware.memorySize))
        """
    def main(self):
#         self.vmGuest()
        self.host_perform()
if __name__ == "__main__":
    vmInfo={}
    vmInfo['ip'] = '10.10.10.64'
    vmInfo['username'] = 'administrator@vsphere.local'
    vmInfo['password'] = 'Kes2719!'
    vmInfo['port'] = '50000'
    vm_Perform(vmInfo).main()
