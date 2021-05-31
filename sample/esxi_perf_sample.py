#!/usr/bin/env python
# William Lam
# www.virtuallyghetto.com

"""
vSphere Python SDK program for demonstrating vSphere perfManager API based on
Rbvmomi sample https://gist.github.com/toobulkeh/6124975
"""

import argparse
import atexit
import getpass
import datetime
from pyVim.connect import SmartConnect, Disconnect
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import ssl

class Perfrom():
    def __init__(self):
        pass
    


    def GetVMHosts(self,content):
        print("Getting all ESX hosts ...")
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj
    
    
    def getSi(self):
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
        return si

    def main(self):
       
        try:
            si=self.getSi()
            
            if not si:
                print("Could not connect to the specified host using specified "
                      "username and password")
                return -1
    
            atexit.register(connect.Disconnect, si)
    
            content = si.RetrieveContent()
            hosts=self.GetVMHosts(content)
            for esxi in hosts:
                print esxi
                search_index = content.searchIndex
                # quick/dirty way to find an ESXi host
                host = search_index.FindByDnsName(dnsName=esxi.name, vmSearch=False)
         
                perfManager = content.perfManager
                
                metricId = vim.PerformanceManager.MetricId(counterId=6, instance="*")
                startTime = datetime.datetime.now() - datetime.timedelta(hours=1)
                endTime = datetime.datetime.now()
         
                query = vim.PerformanceManager.QuerySpec(maxSample=5,
                                                         entity=host,
                                                         metricId=[metricId],
                                                         startTime=startTime,
                                                         endTime=endTime)
         
                result = perfManager.QueryPerf(querySpec=[query])
                for r in result:
                    print r
    
        except vmodl.MethodFault as e:
            print("Caught vmodl fault : " + e.msg)
            return -1
        except Exception as e:
            print("Caught exception : " + str(e))
            return -1
    
        return 0

# Start program
if __name__ == "__main__":
    Perfrom().main()
