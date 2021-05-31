#!/usr/bin/env python
"""
Written by Michael Rice
Github: https://github.com/michaelrice
Website: https://michaelrice.github.io/
Blog: http://www.errr-online.com/
This code has been released under the terms of the Apache-2.0 license
http://opensource.org/licenses/Apache-2.0
"""
from __future__ import print_function

import os
import sys
from pyVim.connect import SmartConnect, Disconnect
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import atexit
import sys
import argparse

# 
# host='10.10.10.64'
# user='administrator@vsphere.local'
# password='Kes2719!'
# 
# context = None
# if hasattr(ssl, '_create_unverified_context'):
#     context = ssl._create_unverified_context()
#     si = SmartConnect(host=host,
#                   user=user,
#                   pwd=password,
#                   sslContext=context)
# 
# 
# atexit.register(Disconnect, si)
# content = si.RetrieveContent()
# containerView = content.viewManager.CreateContainerView(content.rootFolder,
#                                                             [vim.VirtualMachine],
#                               
#                                                             True)
# 
# 
# INDEX = si.content.searchIndex
# print (INDEX)
# uuid='238c3fe4-3a77-11e2-81e9-6cae8b62d8d2'
# uuid='73ef6d84-3a91-11e2-80ab-6cae8b62c58a'
# 
# if INDEX:
#     HOST = INDEX.FindByUuid(datacenter=None, uuid=uuid, vmSearch=False)
#     print (HOST)
#     print (alarm.print_triggered_alarms(entity=HOST))
#     # Since the above method will list all of the triggered alarms we will now
#     # prompt the user for the entity info needed to reset an vcenter_event from red
#     # to green
# #     try:
# #         alarm_mor = raw_input("Enter the alarm_moref from above to reset the "
# #                               "vcenter_event to green: ")
# #     except KeyboardInterrupt:
# #         # this is useful in case the user decides to quit and hits control-c
# #         print()
# #         raise SystemExit
# #     if alarm_mor:
# #         if alarm.reset_alarm(entity_moref=HOST._moId,
# #                              entity_type='HostSystem',
# #                              alarm_moref=alarm_mor.strip(),
# #                              service_instance=si):
# #             print("Successfully reset vcenter_event {0} to green.".format(alarm_mor))
# else:
#     print("Unable to create a SearchIndex.")
    

class HostAlarm():
    def __init__(self):
        pass
    
    def GetVMHosts(self,content):
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj
    
    def main(self):
        host='10.10.10.64'
        user='administrator@vsphere.local'
        pwd='Kes2719!'
        
        
        # Connect to the host without SSL signing
        try:
            si = SmartConnectNoSSL(
                host=host, user=user, pwd=pwd)
            atexit.register(Disconnect, si)
    
        except IOError as e:
            pass
    
        if not si:
            raise SystemExit("Unable to connect to host with supplied info.")
            sys.exit(1)
    
        content = si.RetrieveContent()
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        hosts = self.GetVMHosts(content)
        print (hosts)
