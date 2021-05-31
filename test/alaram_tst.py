'''
Created on 2019. 5. 8.

@author: Administrator
'''
from __future__ import print_function
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
from tools import alarm
from tools import cli



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

root_folder = si.content.rootFolder
# again crude example here. use the logging module instead
print (dir(root_folder))
with open("my_script_log_file.txt", 'a') as f:
    print(root_folder.name, file=f)
    for var, val in os.environ.items():
        # When an vcenter_event is triggered and run a lot of environment variables are set. 
        # This will list them all with their values.
        if var.startswith("VMWARE_ALARM"):
            print("{} = {}".format(var, val), file=f)
    print("##########", file=f)
atexit.register(Disconnect, si)