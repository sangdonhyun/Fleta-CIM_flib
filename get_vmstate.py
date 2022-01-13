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
from _ast import If
data = {}
class VM():
    def __init__(self):
        self.db=fletaDbms.FletaDb()
        self.vmList=[]
        self.oldVmStatus=self.oldVmStatus()
    
    def oldVmStatus(self):
        oldVmStatus={}
        oldVmList=self.db.getList('guest')
        for oldvm in oldVmList:
            oldVmStatus[oldvm[1]]=oldvm[5]
        return oldVmStatus
    
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
        passwd = vmInfo['password']
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
    
    
    def send_snmp(self,smsMsg):
        errDic={}
        errDic['event_date']
        """
            ('1.3.6.1.4.1.6485.1001.0', OctetString(errDic['serial'])),
                    ('1.3.6.1.4.1.6485.1001.1', OctetString(errDic['event_date'])),
                    ('1.3.6.1.4.1.6485.1001.2', OctetString(errDic['event_code'])),
                    ('1.3.6.1.4.1.6485.1001.3', OctetString(errDic['severity'])),
                    ('1.3.6.1.4.1.6485.1001.4', OctetString(errDic['desc'])),
                    ('1.3.6.1.4.1.6485.1001.5', OctetString(errDic['vendor'])),
                    ('1.3.6.1.4.1.6485.1001.6', OctetString(errDic['device_type'])),
                    ('1.3.6.1.4.1.6485.1001.7', OctetString(errDic['method'])),
                    ('1.3.6.1.4.1.6485.1001.8', OctetString(errDic['etc'])),
        """
    def main(self):

        smsList=[]
        vcList=self.getVcList()
        for vc in vcList:
            self.vmStat(vc)
        
        if  self.oldVmStatus == {} :
            self.db.upsert(self.vmList)
        else:
            for vm in self.vmList:
                vm_uuid=vm['vm_uuid']
                print (self.oldVmStatus)
                
                
                    
        
            if not vm_uuid not in self.oldVmStatus.keys():
                msg='new vm geuset (vm name : %s , v-center : %s, ESX : %s)'%(vm['vm_name'],vm['vc_vcenter'],vm['vc_hostserver'])
                smsList.append(msg)
            if vm['vm_uuid'] !=  self.oldVmStatus[vm_uuid]:
                print (vm['vm_name'],vm['vc_vcenter'],vm['vc_hostserver'],self.oldVmStatus[vm_uuid],vm['vm_power'])
                msg='vm geuset (vm name : %s , v-center : %s, ESX : %s) power status has changed %s-> %s' %(vm['vm_name'],vm['vc_vcenter'],vm['vc_hostserver'],self.oldVmStatus[vm_uuid],vm['vm_power'])
                smsList.append(msg)
            self.db.upsert(self.vmList)

            for sms in smsList:
                print (sms)
        
if __name__ == "__main__":
    VM().main()
    