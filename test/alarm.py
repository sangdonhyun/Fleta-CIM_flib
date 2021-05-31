'''
Created on 2019. 5. 8.

@author: Administrator
'''



#!/usr/bin/env python

import pyVmomi
import argparse
import atexit
import itertools
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect
import humanize
import ssl
from datetime import datetime, timedelta
import tools
import json
MBFACTOR = float(1 << 20)

printVM = False
printDatastore = True
printHost = False


def GetArgs():

    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-s', '--host', required=True, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                        help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    args = parser.parse_args()
    return args


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


def fwrite(msg,wbit='a'):
    with open('alarm.txt',wbit) as f:
        f.write(msg+'\n')
#         print msg

def main():
    fwrite('','w')
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
    
    
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()
    am = content.alarmManager
    alarms = am.GetAlarm(content.rootFolder) # get all alarms
    fwrite('###***alarm list***###','w')
    for alarm in alarms:
        print alarm
        print '-'*50
        fwrite(str(alarm.info))
#         try: 
#             # only alarms of type EventAlarms can be unset
#             if isinstance(alarm.info.expression.expression[0], vim.alarm.EventAlarmExpression):
#                 # status can be Normal, Warning, Alert, or Unset. Unset maps to "none"
#                 if alarm.info.expression.expression[0].status == None:
#                     fwrite(str(alarm.info))
#                     print alarm.info
#                     print alarm.info.name
#                     print alarm.info.description
                    
#         except AttributeError, e:
#             None
    
if __name__ == "__main__":
    main()
