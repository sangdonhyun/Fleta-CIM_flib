#-*- coding: utf-8 -*-
'''
Created on 2019. 4. 25.

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
import humanize
import json
import re


reload(sys)
sys.setdefaultencoding('utf8')

class VCenter():
    def __init__(self,vcInfo):
        self.vcInfo=vcInfo
        self.fileName=self.getFileName()
    
    def getNow(self,format='%Y-%m-%d %H:%M:%S'):
        return time.strftime(format)

    def getHeadMsg(self,title='FLETA BATCH LAOD'):
        now = self.getNow()
        msg = '\n'
        msg += '#'*79+'\n'
        msg += '#### '+' '*71+'###\n'
        msg += '#### '+('TITLE     : %s'%title).ljust(71)+'###\n'
        msg += '#### '+('DATA TIME : %s'%now).ljust(71)+'###\n'
        msg += '#### '+('IP        : %s'%self.vcInfo['ip']).ljust(71)+'###\n'
        msg += '#### '+' '*71+'###\n'
        msg += '#'*79+'\n'
        return msg
    
    def getEndMsg(self):
        now = self.getNow()
        msg = '\n'
        msg += '#'*79+'\n'
        msg += '####  '+('END  -  DATA TIME : %s'%now).ljust(71)+'###\n'
        msg += '#'*79+'\n'
        return msg
    
    def getFileName(self):
        fn='%s_%s_test.tmp'%(self.vcInfo['name'],self.vcInfo['ip'])
        fileName=os.path.join('data',fn)
        return fileName
    
    def getSi(self):
        # host = '121.170.193.209'
        # user='administrator@vsphere.local'
        # pwd='Kes2719!'
        # port=50000
        user=self.vcInfo['username']
        host=self.vcInfo['ip']
        pwd=self.vcInfo['password']
        port=int(self.vcInfo['port'])

        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
            si = SmartConnect(host=host,
                          user=user,
                          pwd=pwd,
                          port=port,
                          sslContext=context)
        if not si:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1
        
        atexit.register(Disconnect, si)
        
        
        return si
    def getDataCenter(self,si):
            
            content = si.RetrieveContent()
            # A list comprehension of all the root folder's first tier children...
            datacenters = [entity for entity in content.rootFolder.childEntity
                                      if hasattr(entity, 'vmFolder')]
            for dc in datacenters:
                self.fwrite(str(dc))
                
                
                print dc.name
                msg='DATA CENTER : %s'%str(dc.name)
                self.fwrite(msg)
                datastores = dc.datastore
                for ds in datastores:
                    msg=self.dcDsInfo(ds)
                    
                    self.fwrite(msg)
                
                
                
                
                hostFolder = dc.hostFolder
                self.fwrite('-'*50)
                computeResourceList = hostFolder.childEntity
                print computeResourceList
                self.fwrite('-'*50)
                self.fwrite(computeResourceList)
                for computeResource in computeResourceList:
                    self.fwrite('-'*50)
                    self.fwrite('cluster name :%s'%computeResource.name)
                    self.fwrite(computeResource.summary)
                    self.fwrite('-'*50)
                    self.fwrite('cluster host :')
                    self.fwrite(computeResource.host)
#                     msg=self.dcHostInfo(computeResource)

#                     self.fwrite(msg)
                    print dir(computeResource)
                    hostList = computeResource.host
                    for host in hostList:
                        self.fwrite('-'*50)
                        self.fwrite( host.summary)
                        print host.hardware


                        print (str(host.summary.host))
                        print ('-' * 50)
                        print ('hostname :{}'.format(host.name))
                        print (host.config.storageDevice.scsiLun)

                
                #
                # clusters = dc.hostFolder.childEntity
                # for cluster in clusters:
                #     print cluster
                #     print cluster.name
                #     print cluster.summary
                #     sys.exit()
                    
                    
#                     print dc.val
    def dcHostInfo(self,cr):
        msg=''
#         try:
        hostList = cr.host
        print "##################################################"
        print "Compute resource name: ", cr.name
        print "##################################################"
        for host in hostList:
            msg=self.getHostInfo(host)
#         except Exception as error:
#             print "Unable to access information for compute resource: ",
#             cr.name
#             print error
#             pass
        return msg
    
    def getHostInfo(self,host):
        msg=''
        
        summary = host.summary
        stats = summary.quickStats
        hardware = host.hardware
        print hardware
        cpuUsage = stats.overallCpuUsage
        memoryCapacity = hardware.memorySize
        memoryCapacityInMB = float(hardware.memorySize)/1024
        memoryUsage = stats.overallMemoryUsage
        freeMemoryPercentage = round(100 - (
            (float(memoryUsage/1024) / (memoryCapacity/1024/1024/1024)) * 100
        ),2)
        freeMemorySpace =round(float(memoryCapacity/1024/1024/1024)-(float(memoryUsage/1024)),2)
        
        msg += "-"*50+'\n'
        msg += "Host name: %s \n"%(str(host.name))
        msg += "_"*50+'\n'
        msg += "Host CPU socket count  : %s\n"%(hardware.cpuInfo.numCpuPackages)
        msg += "Host CPU core count    : %s\n"%(hardware.cpuInfo.numCpuCores)
        msg += "Host CPU threads count : %s\n"%(hardware.cpuInfo.numCpuThreads)
        msg += "Host CPU hz            : %s hz\n"%(hardware.cpuInfo.hz)
        msg += "Host CPU total hz      : %s\n"%(int(hardware.cpuInfo.hz)*int(hardware.cpuInfo.numCpuCores))
        msg += "Host CPU Usage hz      : %s hz\n"%(cpuUsage)
        
        msg += "Host memory capacity   : %s GB\n"%(memoryCapacity/1024/1024/1024)
                                                            
        msg += "Host memory usage      : %s GB\n"%(memoryUsage/1024)
        msg += "Free memory space      : %s GB\n"%freeMemorySpace
        msg += "Free memory percentage : %s \n"%(freeMemoryPercentage)
        msg += "-"*50+'\n'
        
        
        return msg
    
    def dcDsInfo(self,datastore):
        msg=''
        
        summary = datastore.summary
        capacity = summary.capacity
        freeSpace = summary.freeSpace
        uncommittedSpace = summary.uncommitted
        freeSpacePercentage = (float(freeSpace) / capacity) * 100
        msg += "-"*50+'\n'
        msg +=  "Datastore name: %s"%(str(summary.name))+'\n'
        msg +=  "Capacity: %s"%(humanize.naturalsize(capacity, binary=True))+'\n'
        if uncommittedSpace is not None:
            provisionedSpace = (capacity - freeSpace) + uncommittedSpace
            msg+= "Provisioned space: %s"%(humanize.naturalsize(provisionedSpace,binary=True))+'\n'
        msg+= "Free space: %s"%(humanize.naturalsize(freeSpace, binary=True))+'\n'
        msg+= "Free space percentage: %s "%(freeSpacePercentage)+'\n'
        msg += "-"*50+'\n'
    
    
        print summary.name,summary.capacity
        return msg
    
    def getDataStore(self,si):
        content = si.RetrieveContent()
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.HostSystem],
                                                          True)
        esxi_hosts = objview.view
        objview.Destroy()
        for esxi_host in esxi_hosts:
            pass
        

    def get_host_vnic(self,hosts):

            for host in hosts:
                print 'hostname :',host.name
                print '-'*50
                print (host.config.network.vnic)


                    
                    
    def PrintVmInfo(self,vm, depth=1):
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
                self.PrintVmInfo(c, depth+1)
                return
        
        # if this is a vApp, it likely contains child VMs
        # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
        if isinstance(vm, vim.VirtualApp):
            vmList = vm.vm
            for c in vmList:
                self.fwrite(str(c))
                self.PrintVmInfo(c, depth + 1)
                return
        
        summary = vm.summary.config
        print summary.uuid,summary.name,summary.vmPathName
        if summary.uuid=='564d32f4-b1f7-3381-d190-e12fc4453185':
            print summary
            self.fwrite(summary)
#         self.fwrite(str(vm.config.hardware.device))
        

    def AllVm(self,si):
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder'):
                datacenter = child
                vmFolder = datacenter.vmFolder
                vmList = vmFolder.childEntity
#                 print (vmList)
                for vm in vmList:
#                     print (vm)
                    self.PrintVmInfo(vm)
    def fwrite(self,msg,wbit='a'):
#         print msg

        if not type(str(msg)) == type('유니코드'):
            msg=unicode(str(msg))

        with open(self.fileName,wbit) as fw:
            fw.write(str(msg)+'\n')
    def GetVMHosts(self,content):
        print("Getting all ESX hosts ...")
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj


    def GetHostsPortgroups(self,hosts):
        print("Collecting portgroups on all hosts. This may take a while ...")
        hostPgDict = {}
        for host in hosts:
#             print (str(host))
            
            self.fwrite(str(host))
            pgs = host.config.network.portgroup
            hostPgDict[host] = pgs
            print("\tHost {} done.".format(host.name))
            self.fwrite(host.name)
            self.fwrite(str(pgs))
        print("\tPortgroup collection complete.")
        
        return hostPgDict
    def GetHostsSwitches(self,hosts):
        hostSwitchesDict = {}
        for host in hosts:
            switches = host.config.network.vswitch
            hostSwitchesDict[host] = switches
            self.fwrite(str(switches))
        return hostSwitchesDict

    def getDataStoreFree(self, si):
        content = si.RetrieveContent()
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.Datastore],
                                                          True)
        dcList = objview.view
        objview.Destroy()
        self.fwrite('-' * 50)
        self.fwrite('datastore  count : {}'.format(len(dcList)))
        self.fwrite('-' * 50)

        for dc in dcList:
            self.fwrite('#datastore : {}'.format(dc.name))
            self.fwrite(dc.summary)
            self.fwrite(dc.host)

    def getEsxiHost(self, si):
        content = si.RetrieveContent()
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.HostSystem],
                                                          True)
        esxi_hosts = objview.view
        objview.Destroy()

        for datacenter in content.rootFolder.childEntity:
            hostFolder = datacenter.hostFolder
            computeResourceList = hostFolder.childEntity
            for computeResource in computeResourceList:
                self.fwrite(str(computeResource))
                print computeResource
                hostList = computeResource.host
                print "##################################################"
                print "Compute resource name: ", computeResource.name
                print "##################################################"
                for host in hostList:
                    self.fwrite(str(host.summary))
                    self.fwrite(str(host.hardware))
                    self.fwrite(str(host.config.network.vnic))
    def GetHardware(self,hosts):
                                                           
        for host in hosts:
            # Print the hosts cpu details
            print(dir(host))
            self.fwrite(str(host.summary))
            # convert CPU to total hz to ghz times numCpuCores
#             print("CPU:", round(((host.hardware.cpuInfo.hz/1e+9)*host.hardware.cpuInfo.numCpuCores),0),"GHz")
            #covert the raw bytes to readable size via convertMemory
#             print("Memory:", convertMemory(host.hardware.memorySize))
    def main(self):
        print self.vcInfo
        title='FCIM V-Center'
        headMsg=self.getHeadMsg(title)
        # self.fwrite(headMsg,'w')
        si = self.getSi()
        content = si.RetrieveContent()

        hosts=self.GetVMHosts(content)

        content = si.RetrieveContent()
        # host = content.searchIndex.FindByDnsName(dnsName="DC0_C0_H0", vmSearch=False)
        # print content
        """
        김은석[eskim] 님의말 : [2021-07-20 16:28:18]
        hostname :
        block =
        id = and  (naa.  or eui. or t10.
['Item', '__add__', '__class__', '__contains__', '__delattr__', '__delitem__', '__delslice__', '__dict__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getslice__', '__gt__', '__hash__', '__iadd__', '__imul__', '__init__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__rmul__', '__setattr__', '__setitem__', '__setslice__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'append', 'count', 'extend', 'index', 'insert', 'pop', 'remove', 'reverse', 'sort']
        """
        # self.getDataStoreFree(si)
        """
        ['AcquireCimServicesTicket', 'Array', 'ConfigureCryptoKey', 'Destroy', 'Destroy_Task', 'Disconnect', 'DisconnectHost_Task', 'EnableCrypto', 'EnterLockdownMode', 'EnterMaintenanceMode', 'EnterMaintenanceMode_Task', 'EnterStandbyMode', 'ExitLockdownMode', 'ExitMaintenanceMode', 'ExitMaintenanceMode_Task', 'ExitStandbyMode', 'PowerDownHostToStandBy_Task', 'PowerUpHostFromStandBy_Task', 'PrepareCrypto', 'QueryConnectionInfo', 'QueryHostConnectionInfo', 'QueryMemoryOverhead', 'QueryMemoryOverheadEx', 'QueryOverhead', 'QueryOverheadEx', 'QueryProductLockerLocation', 'QueryTpmAttestationReport', 'Reboot', 'RebootHost_Task', 'ReconfigureDAS', 'ReconfigureHostForDAS_Task', 'Reconnect', 'ReconnectHost_Task', 'Reload', 'Rename', 'Rename_Task', 'RetrieveFreeEpcMemory', 'RetrieveHardwareUptime', 'SetCustomValue', 'Shutdown', 'ShutdownHost_Task', 'UpdateFlags', 'UpdateIpmi', 'UpdateProductLockerLocation', 'UpdateProductLockerLocation_Task', 'UpdateSystemResources', 'UpdateSystemSwapConfiguration', '_GetMethodInfo', '_GetMethodList', '_GetMoId', '_GetPropertyInfo', '_GetPropertyList', '_GetServerGuid', '_GetStub', '_InvokeAccessor', '_InvokeMethod', '__class__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_methodInfo', '_moId', '_propInfo', '_propList', '_serverGuid', '_stub', '_version', '_wsdlName', 'alarmActionsEnabled', 'answerFileValidationResult', 'answerFileValidationState', 'availableField', 'capability', 'complianceCheckResult', 'complianceCheckState', 'config', 'configIssue', 'configManager', 'configStatus', 'customValue', 'datastore', 'datastoreBrowser', 'declaredAlarmState', 'disabledMethod', 'effectiveRole', 'hardware', 'licensableResource', 'name', 'network', 'overallStatus', 'parent', 'permission', 'precheckRemediationResult', 'recentTask', 'remediationResult', 'remediationState', 'runtime', 'setCustomValue', 'summary', 'systemResources', 'tag', 'triggeredAlarmState', 'value', 'vm']
        """
        self.getEsxiHost_vnic(hosts)
        # for host in hosts:
        #
        #     print dir(host.summary.host)
        #     print '-'*50
        #     print host.summary.host
        #     print '-'*50
        #     print 'hostname :',host.name
        #     # for d in dir(host.config):
        #     #     print d
        #     # print host.config.storageDevice.scsiLun
        #     lun_data = host.config.storageDevice.scsiLun
        #     #.descriptor.id
        #     #['Array', '_GetPropertyInfo', '_GetPropertyList', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_propInfo', '_propList', '_version', '_wsdlName', 'alternateName', 'canonicalName', 'capabilities', 'capacity', 'clusteredVmdkSupported', 'descriptor', 'deviceName', 'devicePath', 'deviceType', 'displayName', 'durableName', 'dynamicProperty', 'dynamicType', 'emulatedDIXDIFEnabled', 'key', 'localDisk', 'lunType', 'model', 'operationalState', 'perenniallyReserved', 'physicalLocation', 'protocolEndpoint', 'queueDepth', 'revision', 'scsiDiskType', 'scsiLevel', 'serialNumber', 'ssd', 'standardInquiry', 'uuid', 'vStorageSupport', 'vendor', 'vsanDiskInfo']
        #     print dir(lun_data)
        #     for lun in lun_data:
        #         print dir(lun)
        #         if 'descriptor' in dir(lun):
        #             print (lun.descriptor)
        #         if 'capacity' in dir(lun):
        #             print (lun.capacity)
            # lines = str(lun_data).splitlines()
            # for line in lines:
            #     if re.search('block =',line):
            #         print line
            #     if re.match('id =',line):
            #         print line


        # print (host.config.network.dnsConfig)
            # print (host.config.storageDevice.hostBusAdapter)
            # print host.config.storageDevice.multipathInfo
            # print host.SerialAttachedTargetTransport
            # print host.FibreChannelHba
            # print host.summary


#         self.fwrite("###***V-Center Info***###")
#         self.fwrite(str(vc))
#         self.fwrite("###***DATA CENTER***###")
#         self.getDataCenter(si)
#         self.fwrite("###***datastore***###")
#         self.getDataStore(si)
#         self.fwrite("###***ESXi HOST***###")
#         self.getEsxiHost(si)
#         self.fwrite("###***NETWORK***###")
#         self.GetHostsPortgroups(hosts)
#         self.fwrite("###***VirtualSwitch***###")
#         self.GetHostsSwitches(hosts)
#         self.fwrite("###***Host HardWare***###")
#         self.GetHardware(hosts)
#         self.fwrite("###***VM Guest***###")
#         self.AllVm(si)
#         endMsg=self.getEndMsg()
#         self.fwrite(endMsg)
# #         socketClient.SocketSender(FILENAME=self.fileName,DIR='nasinfo.SCH').main()
#
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
        hostList=self.getHost()
        for host in hostList:
            VCenter(host).main()


if __name__=='__main__':
    Manager().main()

    # si = SmartConnect(
    #     host='121.170.193.209',
    #     user='administrator@vsphere.local',
    #     pwd='Kes2719!',
    #     port=50000)
    # # disconnect this thing
    # atexit.register(Disconnect, si)
    # uuid ='238c3fe4-3a77-11e2-81e9-6cae8b62d8d2'
    # search_index = si.content.searchIndex
    # vm = search_index.FindByUuid(None, uuid, True)
    # print (vm)