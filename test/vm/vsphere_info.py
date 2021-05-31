'''
Created on 2019. 6. 19.

@author: Administrator
'''
#!/usr/bin/env python

import pyVmomi
import argparse
import atexit
import itertools
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import humanize

MBFACTOR = float(1 << 20)

printVM = False
printDatastore = True
printHost = False



def printHostInformation(host):
    try:
        summary = host.summary
        stats = summary.quickStats
        hardware = host.hardware
        cpuUsage = stats.overallCpuUsage
        memoryCapacity = hardware.memorySize
        memoryCapacityInMB = hardware.memorySize/MBFACTOR
        memoryUsage = stats.overallMemoryUsage
        freeMemoryPercentage = 100 - (
            (float(memoryUsage) / memoryCapacityInMB) * 100
        )
        
        print stats
        print "--------------------------------------------------"
        print "Host name: ", host.name
        print "Host CPU usage: ", cpuUsage
        print "Host memory capacity: ", humanize.naturalsize(memoryCapacity,
                                                             binary=True)
        print "Host memory usage: ", memoryUsage / 1024, "GiB"
        print "Free memory percentage: " + str(freeMemoryPercentage) + "%"
        print "--------------------------------------------------"
    except Exception as error:
        print "Unable to access information for host: ", host.name
        print error
        pass


def printComputeResourceInformation(computeResource):
    try:
        hostList = computeResource.host
        print "##################################################"
        print "Compute resource name: ", computeResource.name
        print "##################################################"
        for host in hostList:
            printHostInformation(host)
    except Exception as error:
        print "Unable to access information for compute resource: ",
        computeResource.name
        print error
        pass


def printDatastoreInformation(datastore):
    try:
        summary = datastore.summary
        capacity = summary.capacity
        freeSpace = summary.freeSpace
        uncommittedSpace = summary.uncommitted
        freeSpacePercentage = (float(freeSpace) / capacity) * 100
        print "##################################################"
        print "Datastore name: ", summary.name
        print "Capacity: ", humanize.naturalsize(capacity, binary=True)
        if uncommittedSpace is not None:
            provisionedSpace = (capacity - freeSpace) + uncommittedSpace
            print "Provisioned space: ", humanize.naturalsize(provisionedSpace,
                                                              binary=True)
        print "Free space: ", humanize.naturalsize(freeSpace, binary=True)
        print "Free space percentage: " + str(freeSpacePercentage) + "%"
        print "##################################################"
    except Exception as error:
        print "Unable to access summary for datastore: ", datastore.name
        print error
        pass


def printVmInformation(virtual_machine, depth=1):
    maxdepth = 10
    if hasattr(virtual_machine, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = virtual_machine.childEntity
        for c in vmList:
            printVmInformation(c, depth + 1)
        return

    try:
        summary = virtual_machine.summary
        print "##################################################"
        print "Name : ", summary.name
        print "MoRef : ", summary.vm
        print "State : ", summary.runtime.powerState
        print "##################################################"
    except Exception as error:
        print "Unable to access summary for VM: ", virtual_machine.name
        print error
        pass


def main():
    vchost='10.10.10.64'
    vcuser='administrator@vsphere.local'
    vcpwd='Kes2719!'
    vcport = 443
    try:
        service_instance = connect.SmartConnectNoSSL(host=vchost,
                                                     user=vcuser,
                                                     pwd=vcpwd,
                                                     port=vcport)
    
        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()

        for datacenter in content.rootFolder.childEntity:
            
            
            if hasattr(datacenter.vmFolder, 'childEntity'):
                hostFolder = datacenter.hostFolder
                computeResourceList = hostFolder.childEntity
                for computeResource in computeResourceList:
                    printComputeResourceInformation(computeResource)

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1
    return 0

if __name__ == "__main__":
    main()