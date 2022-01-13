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
import configparser
from datetime import datetime, timedelta
# import datetime
class HostAlarm():
    def __init__(self,vcInfo):
        self.vcInfo=vcInfo
        self.snmp = fletaSnmp.Load()

    def GetVMHosts(self,content):
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj
    
    
    def GetHostsSwitches(self,hosts):
        hostSwitchesDict = {}
        for host in hosts:
            switches = host.config.network.vswitch
            hostSwitchesDict[host] = switches
        return hostSwitchesDict
    
    
    def getAlarmManager(self,content):
        am = content.alarmManager
        alarms = am.GetAlarm(content.rootFolder)
        return alarms
    
    def getWarningAlarm(self,al,alarmlist):
        for alarm in alarmlist:
            if al == str(alarm):
                obj=alarm
        return obj
    def keyWrite(self,key):
        keyFile=os.path.join('config','alarm_key.txt')
        with open(keyFile,'a') as fw:
            fw.write(key+'\n')
    
    def keyRead(self):
        keyFile=os.path.join('config','alarm_key.txt')
        if os.path.isfile(keyFile):
            with open(keyFile) as f:
                keys=f.read()
            keyList=[]
            for key in keys.splitlines():
                keyList.append(key)
            return keyList
        else:
            return []
        
        
        
    def host_health(self,host):
        health = host.runtime.healthSystemRuntime.systemHealthInfo.numericSensorInfo
        print('Hostname: ' + host.name)
        print('Type: ' + host.hardware.systemInfo.model)
        print('Getting temperature sensor data...\n')
        
        # for i in health:
        #     if i.sensorType == 'temperature':
        #         temp=i.currentReading/100
        #         print(i.name + ' ' + str(temp) + ' ' + i.baseUnits)
        #         print (i)
        return health
    def set_dtime(self,host,dtime):
        dtime_file = os.path.join('config', '{}_h_host_dtime.txt'.format(host))
        with open(dtime_file,'w') as fw:
            fw.write(dtime.strftime('%Y-%m-%d %H:%M:%S'))
        with open(dtime_file, 'r') as fw:
            print fw.read()


    def get_dtime(self,host):
        dtime_file = os.path.join('config','{}_h_host_dtime.txt'.format(host))
        if os.path.isfile(dtime_file):
            try:
                with open(dtime_file) as f:
                    rf= f.read()
                    dtime = datetime.strptime(rf,'%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print str(e)
                dtime = datetime.now()-timedelta(days=30)
        else:
            dtime = datetime.now()-timedelta(days=30)
        return dtime


    def main(self,):
        host=self.vcInfo['ip']
        user=self.vcInfo['username']
        pwd=self.vcInfo['password']
        port = self.vcInfo['port']
        keyList=self.keyRead()
        # Connect to the host without SSL signing
        try:
            si = SmartConnectNoSSL(
                host=host, user=user, pwd=pwd,port=int(port))
            atexit.register(Disconnect, si)
    
        except IOError as e:
            pass
    
        if not si:
            raise SystemExit("Unable to connect to host with supplied info.")
            
    
        content = si.RetrieveContent()
        amList=self.getAlarmManager(content)
        alserialList=[]
        for am in amList:
    #         print am,type(am),str(am)
            alserialList.append(str(am))
            
    #     print alserialList
        
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        
        hosts = self.GetVMHosts(content)
        alList=[]
        for host in hosts:
            # health = self.host_health(host)
            healths = host.runtime.healthSystemRuntime.systemHealthInfo.numericSensorInfo
            host_uuid=host.summary.hardware.uuid
            dtime = self.get_dtime(host.name)
            for i in healths:
                # print '-'*50
                # print(i.name , i.baseUnits,dir(i))
                # print (i.id)
                # print (i.healthState.key)
                # print (i.healthState.summary)
                # print (i)
                # print i.sensorType,i.baseUnits
                event_date = i.timeStamp
                event_date_dt = datetime.strptime(event_date, '%Y-%m-%dT%H:%M:%SZ')
                event_date_str = datetime.strftime(event_date_dt, '%Y-%m-%d %H:%M:%S')
                # print dtime,event_date_dt,dtime > event_date_dt
                if dtime < event_date_dt :

                    etc = "Sensor type :{},Sensor unit :{}, id : {}".format(i.sensorType,i.baseUnits,i.id)
                    errDic = {}
                    errDic['serial']=host_uuid
                    errDic['event_date'] = event_date_str
                    errDic['severity'] = i.healthState.key
                    errDic['desc'] = i.healthState.summary
                    errDic['vendor'] = 'VMware'
                    errDic['device_type'] = 'VCT'
                    errDic['method'] = 'snmp'
                    errDic['event_code'] = i.id
                    errDic['etc'] = etc
                    print (errDic)
                    self.snmp.errSnmpTrapSend(errDic)
            self.set_dtime(host.name,dtime)
                    # errDic['event_date']=i.time.strftime('%Y-%m-%d %H:%M:%S')
                # errDic['event_code']=alarm.key
                # errDic['severity']=alarm.overallStatus
                # errDic['desc']=alInfo.info.description.encode('utf-8')
                # errDic['vendor']='VMware'
                # errDic['device_type']='VCT'
                # errDic['method'] = 'snmp'
                # errDic['etc'] ='%s %s'%(alarm.alarm,alInfo.info.name)
#             host_uuid=host.summary.hardware.uuid
#             INDEX = si.content.searchIndex
#
#             if INDEX:
#                 HOST = INDEX.FindByUuid(datacenter=None, uuid=host_uuid, vmSearch=False)
#                 alarms = HOST.triggeredAlarmState
#
#                 for alarm in alarms:
#
#                     print type(alarm),alarm
#                     event_time = alarm.time
#                     print event_time,type(event_time)
#                     event_time_str = datetime.strftime(event_time,'%Y-%m-%d %H:%M:%S')
# #
#                     if str(alarm.alarm) in alserialList:
#                         event_date_dt = alarm.time
#                         event_date = alarm.time.strftime('%Y-%m-%d %H:%M:%S')
#
#                         alInfo=self.getWarningAlarm(str(alarm.alarm), amList)
#                         errDic={}
#                         errDic['serial']=self.vcInfo['ip']
#                         errDic['event_date']=alarm.time.strftime('%Y-%m-%d %H:%M:%S')
#                         errDic['event_code']=alarm.key
#                         errDic['severity']=alarm.overallStatus
#                         errDic['desc']=alInfo.info.description.encode('utf-8')
#                         errDic['vendor']='VMware'
#                         errDic['device_type']='VCT'
#                         errDic['method'] = 'snmp'
#                         errDic['etc'] ='%s %s'%(alarm.alarm,alInfo.info.name)
#
#                         if str(alarm.key) not in keyList:
#                             # print '-'*50
#                             # print alInfo.info.name
#                             # print alInfo.info.systemName
#                             # print alInfo.info.description
#                             # print alarm.entity
#                             # print alarm.time.strftime('%Y-%m-%d %H:%M:%S')
#                             # print alarm.alarm
#                             # print alarm.overallStatus
#                             # print alarm.key
#                             fletaSnmp.Load().errSnmpTrapSendV2(errDic)
#                             print '-'*50
#                             print 'errDic' ,errDic
#                             self.keyWrite(alarm.key)
#                         # fletaSnmp.Load().errSnmpTrapSendV2(errDic)
# #
                            
                    
        
# Main section

class Manager():
    def __init__(self):
        self.cfg = self.getCFg()
    
    
    def getCFg(self):
        cfg = configparser.RawConfigParser()
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
#     while True:
#         Manager().main()
#         time.sleep(60)
    Manager().main()        
