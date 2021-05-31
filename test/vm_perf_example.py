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
from tools import cli
from pyVim.connect import SmartConnectNoSSL, Disconnect
import atexit
import sys


def main():

    host='10.10.10.64'
    user='administrator@vsphere.local'
    pwd='Kes2719!'

    # Connect to the host without SSL signing
    try:
        si = SmartConnectNoSSL(
            host=host,
            user=user,
            pwd=pwd,
            port=int(443))
        atexit.register(Disconnect, si)

    except IOError as e:
        pass

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

    # Loop through all the VMs
    for child in children:
        print dir(child.summary)
        print child.summary.runtime.powerState
        sys.exit()
        # Get all available metric IDs for this VM
        counterIDs = [m.counterId for m in
                      perfManager.QueryAvailablePerfMetric(entity=child)]

        # Using the IDs form a list of MetricId
        # objects for building the Query Spec
        counterIDs=[2,24]
        metricIDs = [vim.PerformanceManager.MetricId(counterId=c,
                                                     instance="*")
                     for c in counterIDs]

        # Build the specification to be used
        # for querying the performance manager
        spec = vim.PerformanceManager.QuerySpec(maxSample=1,
                                                entity=child,
                                                intervalId=300,
                                                metricId=metricIDs)
        
        # Query the performance manager
        # based on the metrics created above
        result = perfManager.QueryStats(querySpec=[spec])

        # Loop through the results and print the output
        output = ""
        for r in result:
            
            output += "name:        " + child.summary.config.name + "\n"
            output += "uuid:        " + child.summary.config.uuid + "\n"
            for val in result[0].value:
#                 print val
                # python3
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


if __name__ == "__main__":
    main()
