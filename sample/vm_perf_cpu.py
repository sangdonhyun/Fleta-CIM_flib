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
# from tools import cli
from pyVim.connect import SmartConnectNoSSL, Disconnect
import atexit
import os
import sys
import ConfigParser
import time
class VmPerform():
    def __init__(self,host):
        self.host=host
    
    
    
    def main(self):
    
        host='10.10.10.64'
        user='administrator@vsphere.local'
        pwd='Kes2719!'
        
        
        # Connect to the host without SSL signing
        try:
            si = SmartConnectNoSSL(
                host=host, user=user, pwd=pwd)
            atexit.register(Disconnect, si)
    
        except IOError as e:
            pass
    
        if not si:
            raise SystemExit("Unable to connect to host with supplied info.")
#             sys.exit(1)
    
        content = si.RetrieveContent()
        perfManager = content.perfManager
    
        # create a mapping from performance stats to their counterIDs
        # counterInfo: [performance stat => counterId]
        # performance stat example: cpu.usagemhz.LATEST
        # counterId example: 6
        counterInfo = {}
        for c in perfManager.perfCounter:
#             print (str(c))
#             sys.exit()
            
            fullName = c.groupInfo.key + "." + c.nameInfo.key + "." + c.rollupType
            counterInfo[fullName] = c.key
    
        # create a list of vim.VirtualMachine objects so
        # that we can query them for statistics
        container = content.rootFolder
        viewType = [vim.VirtualMachine]
        recursive = True
    
        containerView = content.viewManager.CreateContainerView(container,
                                                                viewType,
                                                                recursive)
        children = containerView.view
#         print children
        
        # Loop through all the VMs
        for child in children:
           
            # Get all available metric IDs for this VM
            counterIDs = [m.counterId for m in
                          perfManager.QueryAvailablePerfMetric(entity=child)]
    
            # Using the IDs form a list of MetricId
            # objects for building the Query Spec
            metricIDs = [vim.PerformanceManager.MetricId(counterId=c,
                                                         instance="*")
                         for c in counterIDs]
    
            # Build the specification to be used
            # for querying the performance manager
#             print "metricIDs :",metricIDs
#             sys.exit()
            spec = vim.PerformanceManager.QuerySpec(maxSample=1,
                                                    entity=child,
                                                    metricId=metricIDs)
            
                
            # Query the performance manager
            # based on the metrics created above
            result = perfManager.QueryStats(querySpec=[spec])
            # Loop through the results and print the output
            output = ""
            for r in result:
#                 print r
                print '-'*50
                uuid= child.summary.config.uuid
                
                output += "name:        " + child.summary.config.name + "\n"
                output += "uuid:        " + uuid + "\n"
                for val in result[0].value:
    #                 print val
                    # python3
                    if uuid=='4200454a-71cf-e743-a780-0032abccf0ad':
                        if sys.version_info[0] > 2:
                            counterinfo_k_to_v = list(counterInfo.keys())[
                                list(counterInfo.values()).index(val.id.counterId)]
                        # python2
                        else:
                            counterinfo_k_to_v = counterInfo.keys()[
                                counterInfo.values().index(val.id.counterId)]
                        if val.id.instance == '':
                            output += "%s: %s\n" % (
                                counterinfo_k_to_v, str(val.value[0]))
                        else:
                            output += "%s (%s): %s\n" % (
                                counterinfo_k_to_v, val.id.instance, str(val.value[0]))
    
            print(output)


class Manager():
    def __init__(self):
        self.cfg = self.getCFg()
    
    
    def getCFg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile= os.path.join('../','config','list.cfg')
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
        print hostList
        for host in hostList:
            while True:
                VmPerform(host).main()
                time.sleep(1)

if __name__ == "__main__":
    Manager().main()
