'''
Created on 2019. 6. 20.

@author: Administrator
'''
import atexit
import argparse
import getpass
import ssl

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

import getpass
import datetime
 
 
def main():
 
    vchost='10.10.10.64'
    vcuser='administrator@vsphere.local'
    vcpwd='Kes2719!'
    vcport = 443
    
    context = None
    if hasattr(ssl, "_create_unverified_context"):
        context = ssl._create_unverified_context()
    si = SmartConnect(host=vchost,
                      user=vcuser,
                      pwd=vcpwd,
                      port=vcport,
                      sslContext=context)
    if not si:
        raise SystemExit("Unable to connect to host with supplied info.")
 
    content = si.RetrieveContent()
    perfManager = content.perfManager
 
    # create a mapping from performance stats to their counterIDs
    # counterInfo: [performance stat => counterId]
    # performance stat example: cpu.usagemhz.LATEST
    # counterId example: 6
    counterInfo = {}
    for c in perfManager.perfCounter:
        prefix = c.groupInfo.key
        fullName = c.groupInfo.key + "." + c.nameInfo.key + "." + c.rollupType
        counterInfo[fullName] = c.key
        #print'fullName {}= {}'.format(fullName,c.key)
  
    # create a list of vim.VirtualMachine objects so
    # that we can query them for statistics
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True
 
    containerView = content.viewManager.CreateContainerView(container,
                                                            viewType,
                                                            recursive)
    children = containerView.view
 
    #startTime = datetime.datetime.now() - datetime.timedelta(hours=24)
    #endTime = datetime.datetime.now()
    # Loop through all the VMs
    for child in children:
        # Get all available metric IDs for this VM
        #counterIDs = [m.counterId for m in
        #              perfManager.QueryAvailablePerfMetric(child,None,None,20)]              
        #print("child counterIDS",counterIDs)
        counterIDs = [146,147,470,471]        
 
        # Using the IDs form a list of MetricId
        # objects for building the Query Spec
        metricIDs = [vim.PerformanceManager.MetricId(counterId=c,
                                                     instance="")
                     for c in counterIDs]
        #print("metricIDs ",metricIDs)
 
        # Build the specification to be used
        # for querying the performance manager
        spec = vim.PerformanceManager.QuerySpec(maxSample=2,
                                                entity=child,
                                                metricId=metricIDs,
                        intervalId=20)
        # Query the performance manager
        # based on the metrics created above
        result = perfManager.QueryStats(querySpec=[spec])
 
        # Loop through the results and print the output
        output = ""
        for r in result:
            #print("the r is ",r)
            output += "name:        " + child.summary.config.name + "\n"
            for val in result[0].value:
                output += counterInfo.keys()[
                          counterInfo.values().index(val.id.counterId)]
                output += ": " + str(val.value[0]) + "\n"
            output += "\n"
 
        print(output)
 
if __name__ == "__main__":
    main()
