'''
Created on 2019. 4. 30.

@author: Administrator
'''
import os
import sys
import ConfigParser
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import argparse
import atexit
import getpass
import ssl
import time
import socketClient
context = None
import datetime

def creationDate(vm):
    print vm.config
    

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
#     print child
    vm = child.summary.config.name
    print vm
    creationDate(child)
#     vmSummary = child.summary
#     print vmSummary
#     print vmSummary.vm.guest
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
