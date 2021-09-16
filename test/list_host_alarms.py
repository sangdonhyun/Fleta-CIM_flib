#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Written by Michael Rice
Github: https://github.com/michaelrice
Website: https://michaelrice.github.io/
Blog: http://www.errr-online.com/
This code has been released under the terms of the Apache-2.0 license
http://opensource.org/licenses/Apache-2.0
"""


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


def getAlarmManager(content):
    am = content.alarmManager
    alarms = am.GetAlarm(content.rootFolder)
    return alarms

def getWarningAlarm(al,alarmlist):
    for alarm in alarmlist:
        if al == str(alarm):
            obj=alarm
    return obj

def main():
    """
    [vcenter1]
ip=121.170.193.209
username=administrator@vsphere.local
password=Kes2719!
port = 50000
    """
    host='121.170.193.209'
    user='administrator@vsphere.local'
    pwd='Kes2719!'
    
    
    # Connect to the host without SSL signing
    try:
        si = SmartConnectNoSSL(
            host=host, user=user, pwd=pwd,port=5000)
        atexit.register(Disconnect, si)

    except IOError as e:
        pass

    if not si:
        raise SystemExit("Unable to connect to host with supplied info.")
        sys.exit(1)

    content = si.RetrieveContent()
    amList=getAlarmManager(content)
    alserialList=[]
    for am in amList:
#         print am,type(am),str(am)
        alserialList.append(str(am))
#     print alserialList
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()
    
    hosts = GetVMHosts(content)
    alList=[]
    for host in hosts:
        host_uuid=host.summary.hardware.uuid
        INDEX = si.content.searchIndex
        if INDEX:
            HOST = INDEX.FindByUuid(datacenter=None, uuid=host_uuid, vmSearch=False)
            alarms = HOST.triggeredAlarmState
            for alarm in alarms:
                print alarm.alarm,str(alarm.alarm) in alserialList#, alarm.alarm in alserialList
#                 print type(alarm),alarm
                if str(alarm.alarm) in alserialList:
                    print '-'*50
                    print alarm.alarm
                    print alarm
                    alInfo=getWarningAlarm(str(alarm.alarm), amList)
                    print alInfo.info.name
                    print alInfo.info.systemName
                    print alInfo.info.description
                    print alarm.entity
                    print alarm.time.strftime('%Y-%m-%d %H:%M:%S')
                    print alarm.alarm
                    print alarm.overallStatus
                    print alarm.key
                    
                    
                    
                    errDic={}
                    errDic['serial']='11111'
                    errDic['event_date']='2019-05-16 15:00:01'
                    errDic['event_code']='0x1234'
                    errDic['severity']='Warning'
                    errDic['desc']='test'
                    errDic['vendor']='VMware'
                    errDic['device_type']='vCenter'
                    errDic['method'] = 'snmp'
                    errDic['etc'] ='test'
                    
                    self.errSnmpTrapSend(errDic)
                    
    for am in amList:
        type(am),am
        
# Main section
if __name__ == "__main__":
    sys.exit(main())
