'''
Created on 2019. 4. 30.

@author: Administrator
'''
import os
import sys
import configparser
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import argparse
import atexit
import getpass
import ssl
import time
import socketClient
service_instance = None
vcenter_host = "10.10.10.64"
vcenter_port = 443
vcenter_username = "administrator@vsphere.local"
vcenter_password = "Kes2719!"
vmName = "vm-45";
context = None

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
containerView = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.VirtualMachine],
                                                            True)
#getting all the VM's from the connection    
children = containerView.view
#going 1 by 1 to every VM
for child in children:
    print child
    vm = child.summary.config.name
    print vm
    vmSummary = child.summary
    print vmSummary
    print vmSummary.vm.guest
#         #check for the VM
#         if(vm == vmName):
#             vmSummary = child.summary
#             #get the diskInfo of the selected VM
#             info = vmSummary.vm.guest.disk
#             #check for the freeSpace property of each disk
#             for each in info:
#                 #To get the freeSPace in GB's
#                 print eash
# #                 diskFreeSpace = int(each.freeSpace)/1024/1024/1024



def host_mem(self):
        hosts = self.hosts_info()
        vc_usage_mem = 0
        vc_all_mem = 0
        for host in hosts:
            # cpu_usage = host.summary.quickStats.overallCpuUsage
            mem_usage = host.summary.quickStats.overallMemoryUsage
            all_mem = host.hardware.memorySize / 1024 / 1024
            vc_usage_mem += mem_usage
            vc_all_mem += all_mem
            print 'host:{0} usage mem��{1}'.format(host.name, mem_usage)
        print 'VC all usage{0}'.format(vc_usage_mem)
        print 'VC��{0}'.format(vc_all_mem)