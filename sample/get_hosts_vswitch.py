#!/usr/bin/env python
"""
Written by nickcooper-zhangtonghao
Github: https://github.com/nickcooper-zhangtonghao
Email: nickcooper-zhangtonghao@opencloud.tech
Note: Example code For testing purposes only
This code has been released under the terms of the Apache-2.0 license
http://opensource.org/licenses/Apache-2.0
"""

from __future__ import print_function
from pyVim.connect import SmartConnect, Disconnect
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import atexit
import sys
import argparse


def GetVMHosts(content):
    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.HostSystem],
                                                        True)
    obj = [host for host in host_view.view]
    host_view.Destroy()
    return obj


def GetHostsSwitches(hosts):
    hostSwitchesDict = {}
    for host in hosts:
        switches = host.config.network.vswitch
        hostSwitchesDict[host] = switches
    return hostSwitchesDict


def main():
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

    hosts = GetVMHosts(content)
    hostSwitchesDict = GetHostsSwitches(hosts)
    print (hostSwitchesDict)
#     for host, vswithes in hostSwitchesDict.items():
#         for v in vswithes:
#             print (v)
            


# Main section
if __name__ == "__main__":
    sys.exit(main())
