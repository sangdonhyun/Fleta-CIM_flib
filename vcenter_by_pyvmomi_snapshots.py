#-*- coding: utf-8 -*-
'''
Created on 2019. 4. 25.

@author: Administrator
'''
import os
import sys
import ConfigParser
from pyVim.connect import SmartConnect, Disconnect,SmartConnectNoSSL
from pyVmomi import vim

import argparse
import atexit
import getpass
import ssl
import time
import socketClient
import re

reload(sys)
sys.setdefaultencoding('utf8')



# reload(sys)
# sys.setdefaultencoding('utf-8')

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
        fn='%s_%s.tmp'%(self.vcInfo['name'],self.vcInfo['ip'])
        fileName=os.path.join('data',fn)
        return fileName
    
    def getSi(self):
        # host='121.170.193.209'
        host=self.vcInfo['ip']
        # user='administrator@vsphere.local'
        user=self.vcInfo['username']
        # password='Kes2719!'
        password=self.vcInfo['password']
        port = int(self.vcInfo['port'])
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()

            # si = SmartConnect(host=host,
            #               user=user,
            #               pwd=password,
            #               port=port,
            #               sslContext=context)
            si = SmartConnectNoSSL(host=host,
                          user=user,
                          pwd=password,
                          port=port)

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
            
            # Just to prove to ourselves we have that list:
            for dc in datacenters:
                self.fwrite(str(dc))

                self.fwrite('*'*50+'\n')
                print dc.name
                msg='DATA CENTER : %s'%str(dc.name)
                self.fwrite(msg)
                datastores = dc.datastore
                for ds in datastores:
                    msg=self.dcDsInfo(ds)
                    
                    self.fwrite(msg)
                
                hostFolder = dc.hostFolder
                computeResourceList = hostFolder.childEntity
                for computeResource in computeResourceList:
                    msg=self.dcHostInfo(computeResource)
                    self.fwrite(msg)
                    
                    
                    
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
        cpuUsage = stats.overallCpuUsage
        memoryCapacity = hardware.memorySize
        try:
            memoryCapacityInMB = float(hardware.memorySize)/1024
        except:
            memoryCapacityInMB = 0
        memoryUsage = stats.overallMemoryUsage
        try:
            freeMemoryPercentage = round(100 - (
                (float(memoryUsage/1024) / (memoryCapacity/1024/1024/1024)) * 100
            ),2)
            freeMemorySpace =round(float(memoryCapacity/1024/1024/1024)-(float(memoryUsage/1024)),2)
        except:
            freeMemoryPercentage = 0
            freeMemorySpace = 0

        msg += "-"*50+'\n'
        msg += str(hardware.cpuInfo)
        msg += str(stats)
        msg += "Host name: %s \n"%(str(host.name))
        msg += "Host CPU socket count  : %s\n"%(hardware.cpuInfo.numCpuPackages)
        msg += "Host CPU core count    : %s\n"%(hardware.cpuInfo.numCpuCores)
        msg += "Host CPU threads count : %s\n"%(hardware.cpuInfo.numCpuThreads)
        msg += "Host CPU hz            : %s\n"%(hardware.cpuInfo.hz)
        msg += "Host CPU total hz      : %s\n"%(int(hardware.cpuInfo.hz)*int(hardware.cpuInfo.numCpuCores))
        msg += "Host CPU Usage Mhz     : %s\n"%(cpuUsage)
        
        msg += "Host memory capacity   : %s \n"%(memoryCapacity)
                                                            
        msg += "Host memory usage(MB)  : %s \n"%(memoryUsage)
        msg += "Free memory space      : %s \n"%freeMemorySpace
        msg += "Free memory percentage : %s \n"%(freeMemoryPercentage)
        msg += "-"*50+'\n'
        
        
        return msg
    
    def dcDsInfo(self,datastore):
        msg=''
        
        summary = datastore.summary
        print dir(summary)
        name = summary.name.encode('utf-8')

        print name,type(name)
        capacity = summary.capacity
        freeSpace = summary.freeSpace
        uncommittedSpace = summary.uncommitted
        try:
            freeSpacePercentage = (float(freeSpace) / capacity) * 100
        except:
            freeSpacePercentage = 0
        msg += "-"*50+'\n'
        msg +=  u"Datastore name: %s"%(summary.name)+'\n'
        msg +=  "Capacity: %s"%(capacity)+'\n'
        if uncommittedSpace is not None:
            provisionedSpace = (capacity - freeSpace) + uncommittedSpace
            msg+= "Provisioned space: %s"%(provisionedSpace)+'\n'
        msg+= "Free space: %s"%(freeSpace)+'\n'
        msg+= "Free space percentage: %s "%(freeSpacePercentage)+'\n'
        msg += "-"*50+'\n'
        print msg
        return msg
    
         
    def getDataStore(self,si):
        content = si.RetrieveContent()
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.HostSystem],
                                                          True)
        esxi_hosts = objview.view
        objview.Destroy()
        for esxi_host in esxi_hosts:
            
            self.fwrite('esxHost :%s'%esxi_host.name)
            self.fwrite(str(esxi_host))
            storage_system = esxi_host.configManager.storageSystem
            host_file_sys_vol_mount_info = storage_system.fileSystemVolumeInfo.mountInfo
            for host_mount_info in host_file_sys_vol_mount_info:
                self.fwrite(str(host_mount_info))
        
        
    def getDataStoreFree(self,si):
        content = si.RetrieveContent()
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.Datastore],
                                                          True)
        dcList=objview.view
        objview.Destroy()
        self.fwrite('-'*50)
        self.fwrite('datastore  count : {}'.format(len(dcList)))
        self.fwrite('-'*50)
        
        
        for dc in dcList:
            self.fwrite('#datastore : {}'.format(dc.name))
            self.fwrite(dc.summary)
            self.fwrite(dc.host)

    def get_host_vnic(self,hosts):

        for host in hosts:
            self.fwrite('hostname : {}'.format(host.name))
            self.fwrite('-'*50)
            self.fwrite (host.config.network.vnic)

    def getEsxiHost(self,si):
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
        try:
            summary = vm.summary
            self.fwrite(summary)
            self.fwrite(vm.config)
        except:
            pass
#         if vm.summary.config.uuid=='564d32f4-b1f7-3381-d190-e12fc4453185':
#             print summary
#             print summary.config.vmPathName

    def get_all_vm_snapshots(slef,vm):
        results = []
        try:
            rootSnapshots = vm.snapshot.rootSnapshotList
        except:
            rootSnapshots = []

        for snapshot in rootSnapshots:
            results.append(snapshot)
            ch_snapshots = self.get_child_snapshots(snapshot)
            results += ch_snapshots

        return results

    def get_child_snapshots(self,snapshot):
        results = []
        snapshots = snapshot.childSnapshotList

        for snapshot in snapshots:
            results.append(snapshot)
            results += self.get_child_snapshots(snapshot)

        return results


    def get_snap_info(self,vm_list):
        for vm in vm_list:
            try:
                rootSnapshots = vm.snapshot.rootSnapshotList
            except:
                rootSnapshots = []
            # print rootSnapshots

            for snapshots in rootSnapshots:
                print snapshots
                print '-' * 49
                # print snapshots.childSnapshotList

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

                    try:
                        rootSnapshots = vm.snapshot.rootSnapshotList
                    except:
                        rootSnapshots = []
                    # print rootSnapshots

                    for snapshots in rootSnapshots:
                        print snapshots
                        print '-' *49
                        # print snapshots.childSnapshotList

    def fwrite(self,msg,wbit='a'):
#         print msg
#         print msg,type(msg),type(msg) == type('유니코드')
        if not type(msg) == type('유니코드'):
            msg=unicode(msg)
        with open(self.fileName,wbit) as fw:
            fw.write(msg+'\n')
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
    
    def GetHardware(self,hosts):
                                                           
        for host in hosts:
            # Print the hosts cpu details
            print(dir(host))
            self.fwrite(str(host.summary))
            # convert CPU to total hz to ghz times numCpuCores
#             print("CPU:", round(((host.hardware.cpuInfo.hz/1e+9)*host.hardware.cpuInfo.numCpuCores),0),"GHz")
            #covert the raw bytes to readable size via convertMemory
#             print("Memory:", convertMemory(host.hardware.memorySize))


    def VMGuestFreeSpace(self,content):
        containerView = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.VirtualMachine],
                                                            True)
        #getting all the VM's from the connection    
        children = containerView.view
        #going 1 by 1 to every VM
        for child in children:
            print child
            self.fwrite(str(child))
            vm = child.summary.config.name
            vmSummary = child.summary
            self.fwrite(str(vmSummary))
            self.fwrite(str(vmSummary.vm.guest))

    def host_scsi_lun(self,hosts):
        for host in hosts:
            self.fwrite(str(host.summary.host))
            self.fwrite('-'*50)
            self.fwrite('hostname :{}'.format(host.name))
            self.fwrite(host.config.storageDevice.multipathInfo)

    def host_hba_info(self,hosts):
        for host in hosts:
            self.fwrite(str(host.summary.host))
            self.fwrite('-'*50)
            self.fwrite('hostname :{}'.format(host.name))
            self.fwrite(host.config.storageDevice.hostBusAdapter)

    def dns_hostname(self,hosts):
        for host in hosts:
            self.fwrite(str(host.summary.host))
            self.fwrite('-'*50)
            self.fwrite('hostname :{}'.format(host.name))
            self.fwrite(host.config.network.dnsConfig)

    def get_scsi_scsiLun(self,hosts):
        for host in hosts:


            self.fwrite('-'*50)
            self.fwrite('hostname :{}'.format(host.name))
            lun_data = host.config.storageDevice.scsiLun
            lines = str(lun_data).splitlines()
            for line in lines:
                if re.search('block =', line):
                    self.fwrite(line)
                if re.search('id =', line):
                    self.fwrite(line)

    def main(self):
        # print self.vcInfo
        title='VNext V-Center'
        headMsg=self.getHeadMsg(title)
        self.fwrite(headMsg,'w')
        si = self.getSi()
        content = si.RetrieveContent()
        hosts=self.GetVMHosts(content)
        vc= si.content.about
        self.fwrite("###***vCenter Host Spec Info***###")
        self.dns_hostname(hosts)
        self.fwrite("###***V-Center Info***###")
        self.fwrite(str(vc))
        self.fwrite("###***VM SNAPSHOST***###")
        self.AllVm(si)

        endMsg=self.getEndMsg()
        self.fwrite(endMsg)
        socketClient.SocketSender(FILENAME=self.fileName,DIR='vnext\\vcenter').main()
        
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
