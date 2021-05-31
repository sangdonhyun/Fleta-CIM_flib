'''
Created on 2019. 4. 26.

@author: Administrator
'''
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import atexit
import sys
import ssl

def main():
    """
   Simple command-line program demonstrating vSphere perfManager API
   """
 
    
    try:
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port))
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1
 
        atexit.register(connect.Disconnect, service_instance)
 
        content = service_instance.RetrieveContent()
 
        search_index = content.searchIndex
        # quick/dirty way to find an ESXi host
        host = search_index.FindByDnsName(dnsName=args.vihost, vmSearch=False)
 
        perfManager = content.perfManager
        metricId = vim.PerformanceManager.MetricId(counterId=6, instance="*")
        startTime = datetime.datetime.now() - datetime.timedelta(hours=1)
        endTime = datetime.datetime.now()
 
        query = vim.PerformanceManager.QuerySpec(maxSample=1,
                                                 entity=host,
                                                 metricId=[metricId],
                                                 startTime=startTime,
                                                 endTime=endTime)
 
        print(perfManager.QueryPerf(querySpec=[query]))
 
    except vmodl.MethodFault as e:
        print("Caught vmodl fault : " + e.msg)
        return -1
    except Exception as e:
        print("Caught exception : " + str(e))
        return -1
 
    return 0