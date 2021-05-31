#!/usr/bin/python

"""
Python program for listing recent vCenter tasks in a very basic way
"""

from optparse import OptionParser, make_option
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vmodl
from pyVmomi import vim
import pyVmomi
import textwrap
import argparse
import atexit
import time
import math
import sys
import os
import ssl

def main():

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
    print content.taskManager
    
    print len(content.taskManager.recentTask)
    
    
    for task in content.taskManager.recentTask:
        
        print (task.info)
        print (task.moId)
        task.info.reason.userName,
        task.info.entityName,
        task.info.descriptionId,
        task.info.state
    tfs = vim.TaskFilterSpec()
    task_collector = content.taskManager.CreateCollectorForTasks(tfs)
    print dir(task_collector)
# Start program
if __name__ == "__main__":
   main()
