#!/usr/bin/env python
# VMware vSphere Python SDK
# Copyright (c) 2008-2013 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python program for listing the vms on an ESX / vCenter host
"""

import atexit

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import datetime
import sys
# import tools.cli as cli


def print_vm_info(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    vmInfo={}
    summary = virtual_machine.summary
    print("Name       : ", summary.config.name)
#     print("Template   : ", summary.config.template)
#     print("Path       : ", summary.config.vmPathName)
#     print("Guest      : ", summary.config.guestFullName)
#     print("Instance UUID : ", summary.config.instanceUuid)
#     print("Bios UUID     : ", summary.config.uuid)
    vmInfo['name']=summary.config.name
    vmInfo['path']=summary.config.vmPathName
    vmInfo['guest']=summary.config.guestFullName
    vmInfo['uuid'] =summary.config.uuid
    
    annotation = summary.config.annotation
    if annotation:
        print("Annotation : ", annotation)
    print("State      : ", summary.runtime.powerState)
    vmInfo['state'] =summary.runtime.powerState
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        tools_version = summary.guest.toolsStatus
        if tools_version is not None:
#             print("VMware-tools: ", tools_version)
            vmInfo['VMware-tools']=tools_version
        else:
#             print("Vmware-tools: None")
            vmInfo['VMware-tools']=None
        if ip_address:
#             print("IP         : ", ip_address)
            vmInfo['IP'] = ip_address
        else:
#             print("IP         : None")
            vmInfo['IP']=None
    if summary.runtime.question is not None:
        print("Question  : ", summary.runtime.question.text)
    print("")
    return vmInfo



def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """

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

        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)
        perfManager = content.perfManager
        cInfo={}
        netcids=[]
        for c in perfManager.perfCounter:
            fullName = c.groupInfo.key + "." + c.nameInfo.key + "." + c.rollupType
            
            cInfo[c.key]=fullName
            if 'net' in fullName:
                netcids.append(c.key) 
        
        

        vmList=[]
        children = containerView.view
        
        timenow=datetime.datetime.now()
        startTime = timenow - datetime.timedelta(seconds=20)
        
        
        
        for child in children:
            print perfManager.QueryAvailablePerfMetric(entity=child)
            
            vmInfo=print_vm_info(child)
            print vmInfo['state']
            if vmInfo['state'] == 'poweredOn':
#                 print vmInfo
                vmList.append(vmInfo['uuid'])
                counterIDs = [m.counterId for m in perfManager.QueryAvailablePerfMetric(entity=child)]
                metricIDs = [vim.PerformanceManager.MetricId(counterId=c,instance="*")  for c in counterIDs]
                spec = vim.PerformanceManager.QuerySpec(maxSample=1,
                                                    entity=child,
                                                    metricId=metricIDs,
                                                    intervalId=20,
                                                    startTime=startTime)
                                                    
                result = perfManager.QueryStats(querySpec=[spec])
                output=''
                for r in result:
                    print '-'*50
                    uuid= child.summary.config.uuid
                    print "name:        " + child.summary.config.name + "\n"
                    print "uuid:        " + uuid + "\n"
                    for val in result[0].value:
                        countId=val.id.counterId
                        name=cInfo[countId]
                        instance=val.id.instance
                        
                        print name,val.value[0],'counterid :',countId,instance
        
        print vmList
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()
