#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Written by nickcooper-zhangtonghao
Github: https://github.com/nickcooper-zhangtonghao
Email: nickcooper-zhangtonghao@opencloud.tech
Note: Example code For testing purposes only
This code has been released under the terms of the Apache-2.0 license
http://opensource.org/licenses/Apache-2.0
"""

import os
from pyVim.connect import SmartConnect, Disconnect
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import atexit
import sys
import argparse
import fletaSnmp
import ConfigParser
import datetime

class HostAlarm():
    def __init__(self,vcInfo):
        self.vcInfo=vcInfo
    def GetVMHosts(self,content):
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj
        
    def host_health(self,host):
        health = host.runtime.healthSystemRuntime.systemHealthInfo.numericSensorInfo

        print('Hostname: ' + host.name)
        print('Type: ' + host.hardware.systemInfo.model)
        print('Getting temperature sensor data...\n')
#         print health
        print host.name
        print host.summary.hardware.uuid
        print host.summary
        for i in health:
            
            print i.sensorType
            print i.healthState.label
            if i.healthState.label == 'Green':
#                 print i
                errDic={}
                errDic['serial']=host.name
                print type(i.timeStamp)
#                 errDic['event_date']=datetime.datetime.strptime(i.timeStamp,'%Y-%m-%dT%H:%M:%SZ')
                errDic['event_date']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                errDic['event_code']='%s_helth_check'%i.sensorType
                errDic['severity']=i.healthState.label
                msg='%s %s'%(i.name,i.healthState.summary)
                try:
                    currentReading=i.currentReading
                    msg=msg+' currentReading :%s'%currentReading
                except:
                    pass
                errDic['desc']=msg
                errDic['vendor']='VMware'
                errDic['device_type']='VCT'
                errDic['method'] = 'snmp'
                errDic['etc'] ='SENSOR TYPE : %s, ID : %s'%(i.sensorType,i.id)
                print errDic
                fletaSnmp.Load().errSnmpTrapSend(errDic)
                
                
    def main(self,):
#         host='10.10.10.64'
#         user='administrator@vsphere.local'
#         pwd='Kes2719!'
        
        host=self.vcInfo['ip']
        user=self.vcInfo['username']
        pwd=self.vcInfo['password']
        port=self.vcInfo['port']

        
        # Connect to the host without SSL signing
        try:
            si = SmartConnectNoSSL(
                host=host, user=user, pwd=pwd, port=int(port))
            atexit.register(Disconnect, si)
    
        except IOError as e:
            pass
    
        if not si:
            raise SystemExit("Unable to connect to host with supplied info.")
            sys.exit(1)
    
        content = si.RetrieveContent()
        atexit.register(Disconnect, si)
        hosts = self.GetVMHosts(content)
        for host in hosts:
            print 'host health info'
            self.host_health(host)
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
            HostAlarm(host).main()
            
if __name__ == "__main__":
    import time
    Manager().main()
#     while True:
#         Manager().main()
#         time.sleep(60)
        
