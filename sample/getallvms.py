#!/usr/bin/env python
# VMware vSphere Python SDK
# Copyright (c) 2008-2015 VMware, Inc. All Rights Reserved.
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

from __future__ import print_function

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import argparse
import atexit
import getpass
import ssl



def PrintVmInfo(vm, depth=1):
    """
    Print information for a particular virtual machine or recurse into a folder
    or vApp with depth protection
    """
    maxdepth = 10
    
    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm, 'childEntity'):
        if depth > maxdepth:
            return      
        vmList = vm.childEntity
        for c in vmList:
            PrintVmInfo(c, depth+1)
            return
    
    # if this is a vApp, it likely contains child VMs
    # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
    if isinstance(vm, vim.VirtualApp):
        vmList = vm.vm
        for c in vmList:
            print (c)
            PrintVmInfo(c, depth + 1)
            return
    
    summary = vm.summary
    """
    'annotation', 'cpuReservation', 'dynamicProperty', 'dynamicType', 'ftInfo', 'guestFullName', 'guestId', 'installBootRequired', 
    'instanceUuid', 'managedBy', 'memoryReservation', 'memorySizeMB', 'name', 'numCpu', 'numEthernetCards', 'numVirtualDisks',
     'numVmiopBackings', 'product', 'template', 'tpmPresent', 'uuid', 'vmPathName']
    """
    print("Name             : ", summary.config.name)
    print("Path             : ", summary.config.vmPathName)
    print("Guest            : ", summary.config.guestFullName)
    print("guestId          : ", summary.config.guestId)
    print("instanceUuid     : ", summary.config.instanceUuid)
    print("numCpu           : ", summary.config.numCpu)
    print("numEthernetCards : ", summary.config.numEthernetCards)
    print("numVirtualDisks  : ", summary.config.numVirtualDisks)
    print("numVmiopBackings : ", summary.config.numVmiopBackings)
    print("product          : ", summary.config.product)
    print("template         : ", summary.config.template)
    print("tpmPresent       : ", summary.config.tpmPresent)
    print("uuid             : ", summary.config.uuid)
    print (summary.guest)
    print (dir(summary))
    print (summary)
    annotation = summary.config.annotation
    if annotation != None and annotation != "":
        print("Annotation : ", annotation)
    print("State      : ", summary.runtime.powerState)
    if summary.guest != None:
        ip = summary.guest.ipAddress
        if ip != None and ip != "":
            print("IP         : ", ip)  
    if summary.runtime.question != None:
        print("Question  : ", summary.runtime.question.text)
    print("")

def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """
    
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
    if not si:
        print("Could not connect to the specified host using specified "
              "username and password")
        return -1
    
    atexit.register(Disconnect, si)
    
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
            print (vmList)
            for vm in vmList:
                print (vm)
                PrintVmInfo(vm,2)
    
    aboutInfo=si.content.about
    print ('# VCENTER INfO')
    print ('-'*50)
    print("Product Name         :",aboutInfo.name)
    print("Product fullName     :",aboutInfo.fullName)
    print("Product Build        :",aboutInfo.build)
    print("Product Unique Id    :",aboutInfo.instanceUuid)
    print("Product Base OS      :",aboutInfo.osType)
    print("Product vendor       :",aboutInfo.vendor)
    print("Product version      :",aboutInfo.version)
    print("Product localeVersion:",aboutInfo.localeVersion )
    print("Product ins produc   :",aboutInfo.licenseProductName )
    print ('-'*50)
    
        # Search for all ESXi hosts
    objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                      [vim.HostSystem],
                                                      True)
    esxi_hosts = objview.view
    objview.Destroy()

    datastores = {}
    
    print (esxi_hosts)
    for esxi_host in esxi_hosts:
            
            print("{}\t{}\t\n".format("ESXi Host:    ", esxi_host.name))

            # All Filesystems on ESXi host
            storage_system = esxi_host.configManager.storageSystem
            print (dir(storage_system))
            print (storage_system.fileSystemVolumeInfo)
            print (storage_system.storageDeviceInfo)
            host_file_sys_vol_mount_info = \
                storage_system.fileSystemVolumeInfo.mountInfo
            print (dir(storage_system.fileSystemVolumeInfo.volumeTypeList))
            datastore_dict = {}
            # Map all filesystems
            for host_mount_info in host_file_sys_vol_mount_info:
                # Extract only VMFS volumes
                if host_mount_info.volume.type == "VMFS":

                    extents = host_mount_info.volume.extent
            
            
#                     print (dir(host_mount_info.mountInfo))
                    datastore_details = {
                        'uuid': host_mount_info.volume.uuid,
                        'capacity': host_mount_info.volume.capacity,
                        'vmfs_version': host_mount_info.volume.version,
                        'local': host_mount_info.volume.local,
                        'ssd': host_mount_info.volume.ssd,
                        
                    }
                    print (datastore_details)
#                     print (dir(host_mount_info.volume))
                    extent_arr = []
                    extent_count = 0
                    for extent in extents:

                        print("{}\t{}\t".format(
                            "Extent[" + str(extent_count) + "]:",
                            extent.diskName))
#                         print (dir(extent))
#                         print (extent.dynamicType)
#                         print (extent.partition)
#                         print (extent.dynamicProperty)
                        extent_count += 1


            # associate ESXi host with the datastore it sees
            datastores[esxi_host.name] = datastore_dict
    return 0    
    
# Start program
if __name__ == "__main__":
    main()
