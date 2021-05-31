'''
Created on 2019. 5. 20.

@author: Administrator
'''
import os
import sys
import ConfigParser
from pyVim.connect import SmartConnect, Disconnect
from pyVim import connect
from pyVmomi import vim
from pyVim import connect

import argparse
import atexit
import getpass
import ssl
import time
import socketClient
import humanize
import redis_conn
import datetime


class Vm():
    def __init__(self,vmInfo):
        self.vmInfo=vmInfo
        self.r=redis_conn.Redis().r
    
    
    def getSi(self):
        host=self.vmInfo['ip']
        user=self.vmInfo['username']
        password=self.vmInfo['password']
        port = self.vmInfo['port']
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
            si = SmartConnect(host=host,
                          user=user,
                          pwd=password,
                          port = int(port),
                          sslContext=context)
        if not si:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1
        
        atexit.register(Disconnect, si)
        return si
        
    def AllVm(self,si):
        uuidList=[]
        si=self.getSi()
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder'):
                datacenter = child
                vmFolder = datacenter.vmFolder
                vmList = vmFolder.childEntity
                print (vmList)
                for vm in vmList:
                    print vm
                    try:
#                         print vm.summary.config.uuid
                        uuidList.append(vm.summary.config.uuid)
                    except:
                        pass
        return uuidList

    def get_vm__info(self,vm):
        """
        Print information for a particular virtual machine or recurse into a
        folder with depth protection
        """
        vmInfo={}
        summary = vm.summary
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

    def main(self):
        si=self.getSi()
        atexit.register(connect.Disconnect, si)
        content = si.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)
        perfManager = content.perfManager
        self.cInfo={}
        for c in perfManager.perfCounter:
            fullName = c.groupInfo.key + "." + c.nameInfo.key + "." + c.rollupType
            
            self.cInfo[c.key]=fullName
        children = containerView.view
        timenow=datetime.datetime.now()
        startTime = timenow - datetime.timedelta(seconds=20)
        for child in children:
            print 'child :',child
            vmInfo=self.get_vm__info(child)
            counterIDs = [m.counterId for m in perfManager.QueryAvailablePerfMetric(entity=child)]
            metricIDs = [vim.PerformanceManager.MetricId(counterId=c,instance="*")  for c in counterIDs]
#             print vmInfo
            print counterIDs
#             print metricIDs
            sys.exit()
            
            spec = vim.PerformanceManager.QuerySpec(maxSample=1,
                                                entity=child,
                                                metricId=metricIDs,
                                                intervalId=20,
                                                startTime=startTime,
                                                endTime=timenow)
                                                
            result = perfManager.QueryStats(querySpec=[spec])
            output=''
            for r in result:
                print '-'*50
                print r
                uuid= child.summary.config.uuid
                print "name:        " + child.summary.config.name + "\n"
                print "uuid:        " + uuid + "\n"
                for val in result[0].value:
                    countId=val.id.counterId
                    name=self.cInfo[countId]
                    instance=val.id.instance
                    
                    print name,val.value[0],'counterid :',countId,instance
                        
            
        
class Manager():
    def __init__(self):
        self.cfg = self.getCFg()
    
    
    def getCFg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile= os.path.join('config','list.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def getHost(self):
        hostList=[]
        for sec in self.cfg.sections():
            host={}
            host['name'] = sec
            
            for opt in self.cfg.options(sec):
                host[opt] = self.cfg.get(sec,opt)
            hostList.append(host)
        return hostList
    
    
    def main(self):
        print 'v-center vm perform'
        hostList=self.getHost()
        for host in hostList:
            print host
            Vm(host).main()

if __name__ == "__main__":
#     while True:
    Manager().main()
#         time.sleep(5)