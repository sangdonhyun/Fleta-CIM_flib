#-*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Written by Chris Hupman
Github: https://github.com/chupman/
Example: Get guest info with folder and host placement

"""

from __future__ import print_function

from pyVmomi import vim

from pyVim.connect import SmartConnectNoSSL, Disconnect

import argparse
import atexit
import getpass
import json
import configparser
import os
import datetime
import fletaDbms
import fletaSnmp
from _ast import If
import ins_vnstat_guest
data = {}
class VM():
    def __init__(self):
        self.db=fletaDbms.FletaDb()
        self.vmList=[]

        self.snmp=fletaSnmp.Load()
    
    def oldVmStatus(self):
        oldVmStatus={}
        oldVmList=self.db.getList('guest')
        if not oldVmList == None:
            for oldvm in oldVmList:
                oldVmStatus[oldvm[1]]=oldvm[5]
            return oldVmStatus
        else:
            return {}
    
    def getNICs(self,summary, guest):
        nics = {}
        for nic in guest.net:
            if nic.network:  # Only return adapter backed interfaces
                if nic.ipConfig is not None and nic.ipConfig.ipAddress is not None:
                    nics[nic.macAddress] = {}  # Use mac as uniq ID for nic
                    nics[nic.macAddress]['netlabel'] = nic.network
                    ipconf = nic.ipConfig.ipAddress
                    i = 0
                    nics[nic.macAddress]['ipv4'] = {}
                    for ip in ipconf:
                        if ":" not in ip.ipAddress:  # Only grab ipv4 addresses
                            nics[nic.macAddress]['ipv4'][i] = ip.ipAddress
                            nics[nic.macAddress]['prefix'] = ip.prefixLength
                            nics[nic.macAddress]['connected'] = nic.connected
                    i = i+1
        return nics
    
    
    def vmStat(self,vmInfo):
        
        """
        Iterate through all datacenters and list VM info.
        """
        vc_ip = vmInfo['ip']
        user = vmInfo['username']
        passwd=vmInfo['password']
        port = vmInfo['port']

        vmstatList=[]
        vmSMSList=[]
        si = SmartConnectNoSSL(host=vc_ip,
                               user=user,
                               pwd=passwd,
                               port=int(port))
        if not si:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1
    
        atexit.register(Disconnect, si)
    
        content = si.RetrieveContent()
        children = content.rootFolder.childEntity
        status_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for child in children:  # Iterate though DataCenters
            dc = child
            data[dc.name] = {}  # Add data Centers to data dict
            clusters = dc.hostFolder.childEntity
            for cluster in clusters:  # Iterate through the clusters in the DC
                # Add Clusters to data dict
                data[dc.name][cluster.name] = {}
                hosts = cluster.host  # Variable to make pep8 compliance
                for host in hosts:  # Iterate through Hosts in the Cluster
                    hostname = host.summary.config.name
                    # Add VMs to data dict by config name
                    data[dc.name][cluster.name][hostname] = {}
                    
                    vms = host.vm
                    for vm in vms:  # Iterate through each VM on the host
#                         vmname = vm.summary.config.name
                        vmstat={}
                        summary=vm.summary
#                         print ('-'*50)
#                         print (summary.config.uuid)
#                         print (summary.config.name)
#                         print (summary.guest.hostName)
#                         print (summary.guest.ipAddress)
#                         print (summary.runtime.powerState)
#                         print (hostname)
                        vm_uuid=summary.config.uuid
                        power = summary.runtime.powerState
                        vmstat['status_date'] =status_date
                        vmstat['vm_uuid'] =vm_uuid
                        vmstat['vm_name']=summary.config.name
                        vmstat['vm_hostname']=summary.guest.hostName
                        vmstat['vm_ip']=summary.guest.ipAddress
                        vmstat['vm_power']= power
                        vmstat['vc_vcenter'] = vc_ip
                        vmstat['vc_hostserver'] = hostname
                        self.vmList.append(vmstat)
                          
    
    def getVcList(self):
        cfg=configparser.RawConfigParser()
        cfgFile=os.path.join('config','list.cfg')
        cfg.read(cfgFile)
        vcList=[]
        for sec in cfg.sections():
            vc={}
            vc['name']=sec
            for opt in cfg.options(sec):
                vc[opt]=cfg.get(sec,opt)
            vcList.append(vc)
        return vcList
    
    def snmp_send(self,smsInfo):
        
        errDic={}
        errDic['serial']=smsInfo['vm_uuid']
        errDic['event_date']=smsInfo['status_date']
        errDic['event_code']='vm-esx001'
        errDic['severity']='Warning'
        errDic['desc']=smsInfo['desc']
        errDic['vendor']='VMware'
        errDic['device_type']='vm gueset'
        errDic['method'] = 'snmp'
        errDic['etc'] =str(smsInfo)
        # print (errDic)
        self.snmp.errSnmpTrapSendV2(errDic)

    
    def main(self):
        print ('vm status start..')
        smsList=[]
        vcList=self.getVcList()

        for vc in vcList:
            try:
                self.vmStat(vc)
            except Exception as e:
                print (str(e))



        vcList = self.getVcList()

        self.oldVmStatus = self.oldVmStatus()
        print ('vm count :',len(self.oldVmStatus))
        if  self.oldVmStatus == {} :
            self.db.upsert(self.vmList)
            return None
        else:
            for vm in self.vmList:
                vm_uuid=vm['vm_uuid']
                # print (vm_uuid)
                    
        
                if vm_uuid not in self.oldVmStatus.keys():
    #                 msg='new vm geuset (vm name : %s , v-center : %s, ESX : %s)'%(vm['vm_name'],vm['vc_vcenter'],vm['vc_hostserver'])
                    msg="[MXG SMS] vmweare Server Alert: new vm geuset (vm name : %s , v-center : %s, ESX : %s)  %s "%(vm['vm_name'],vm['vc_vcenter'],vm['vc_hostserver'],vm['vm_power']) 
                    smsList.append(msg)
                    vm['desc']=msg
                    self.snmp_send(vm)


                # print (self.oldVmStatus[vm_uuid],vm['vm_uuid'],vm['vm_power'] == self.oldVmStatus[vm_uuid])
                # print (vm)
                if not vm['vm_power'] == self.oldVmStatus[vm_uuid]:
                    # print (vm['vm_name'],vm['vc_vcenter'],vm['vc_hostserver'],self.oldVmStatus[vm_uuid],vm['vm_power'])
                    msg='[MXG SMS] vmweare Server Alert: vm geuset (vm name : %s , v-center : %s, ESX : %s) power status has changed %s-> %s'%(vm['vm_name'],vm['vc_vcenter'],vm['vc_hostserver'],self.oldVmStatus[vm_uuid],vm['vm_power'])
                    smsList.append(msg)
                    vm['desc']=msg

                    self.snmp_send(vm)
                    
        self.db.upsert(self.vmList)
        print ('END vm staus')
        return smsList
if __name__ == "__main__":
    VM().main()
    