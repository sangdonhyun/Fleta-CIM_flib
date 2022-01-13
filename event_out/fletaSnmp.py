'''
Created on 2019. 5. 16.

@author: Administrator
'''
'''
Created on 2018. 11. 5.

@author: user
'''
import os
import re
import sys
import configparser
import glob
import time
from time import strftime, localtime, time
import datetime
from pysnmp.hlapi import *
import serial


class Load():
    def __init__(self):
        self.cfg = self.get_cfg()

    def get_cfg(self):
        cfg = configparser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def errSnmpTrapSendV2(self,errDic):
        try:
            snmp_ip = self.cfg.get('server', 'snmp_ip')
        except :
            snmp_ip = 'localhost'
        print snmp_ip
        iterator = sendNotification(
            SnmpEngine(),
            CommunityData('public', mpModel=0),
            UdpTransportTarget((snmp_ip, 162)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity('1.3.6.1.4.1.6485.901'),
            ).addVarBinds(
                ('1.3.6.1.4.1.6485.1001.0', OctetString(errDic['serial'])),
                ('1.3.6.1.4.1.6485.1001.1', OctetString(errDic['event_date'])),
                ('1.3.6.1.4.1.6485.1001.2', OctetString(errDic['event_code'])),
                ('1.3.6.1.4.1.6485.1001.3', OctetString(errDic['severity'])),
                ('1.3.6.1.4.1.6485.1001.4', OctetString(errDic['desc'])),
                ('1.3.6.1.4.1.6485.1001.5', OctetString(errDic['vendor'])),
                ('1.3.6.1.4.1.6485.1001.6', OctetString(errDic['device_type'])),
                ('1.3.6.1.4.1.6485.1001.7', OctetString(errDic['method'])),
                ('1.3.6.1.4.1.6485.1001.8', OctetString(errDic['etc'])),
            ).loadMibs(
                'SNMPv2-MIB'
            )
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            print(errorIndication)

    def errSnmpTrapSend(self,errDic):
        cfg=configparser.RawConfigParser()
        cfgFile='config\\config.cfg'
        cfg.read(cfgFile)
        print os.path.isfile(cfgFile)
        try:
            snmp_ip=cfg.get('server','snmp_ip')
        except:
            snmp_ip='localhost'
        
        print snmp_ip
        
        
        """
        -v 1.3.6.1.4.1.6485.1001.0 STRING 1234567                            <== serial
        -v 1.3.6.1.4.1.6485.1001.1 STRING 2019-02-26 02:02:01             <== event_date
        -v 1.3.6.1.4.1.6485.1001.2 STRING 0x1234                              <== event_code
        -v 1.3.6.1.4.1.6485.1001.3 STRING Warning                             <== severity
        -v 1.3.6.1.4.1.6485.1001.4 STRING This is test message              <== desc
        -v 1.3.6.1.4.1.6485.1001.5 STRING EMC                                 <== vendor
        -v 1.3.6.1.4.1.6485.1001.6 STRING STG                                  <== device_type
        -v 1.3.6.1.4.1.6485.1001.7 STRING realtime ssh                                  <== method
        -v 1.3.6.1.4.1.6485.1001.8 STRING etc                                  <== etc
        """
        
        errorIndication, errorStatus, errorIndex, varBinds = next(
            sendNotification(
                SnmpEngine(),
                CommunityData('public', mpModel=0),
                UdpTransportTarget((snmp_ip, 162)),
                ContextData(),
                'trap',
                NotificationType(
                    ObjectIdentity('1.3.6.1.4.1.6485.1001'),
                ).addVarBinds(
                    ('1.3.6.1.4.1.6485.1001.0', OctetString(errDic['serial'])),
                    ('1.3.6.1.4.1.6485.1001.1', OctetString(errDic['event_date'])),
                    ('1.3.6.1.4.1.6485.1001.2', OctetString(errDic['event_code'])),
                    ('1.3.6.1.4.1.6485.1001.3', OctetString(errDic['severity'])),
                    ('1.3.6.1.4.1.6485.1001.4', OctetString(errDic['desc'])),
                    ('1.3.6.1.4.1.6485.1001.5', OctetString(errDic['vendor'])),
                    ('1.3.6.1.4.1.6485.1001.6', OctetString(errDic['device_type'])),
                    ('1.3.6.1.4.1.6485.1001.7', OctetString(errDic['method'])),
                    ('1.3.6.1.4.1.6485.1001.8', OctetString(errDic['etc'])),
                    
                )
            )
        )
        if errorIndication:
            print(errorIndication)
    
            


    def errSnmpTrapSendV3(self,errDic):
        cfg=configparser.RawConfigParser()
        cfgFile='config\\config.cfg'
        cfg.read(cfgFile)
        print os.path.isfile(cfgFile)
        try:
            snmp_ip=cfg.get('server','snmp_ip')
        except:
            snmp_ip='localhost'
        
        print snmp_ip
        
        
        """
        -v 1.3.6.1.4.1.6485.1001.0 STRING 1234567                            <== serial
        -v 1.3.6.1.4.1.6485.1001.1 STRING 2019-02-26 02:02:01             <== event_date
        -v 1.3.6.1.4.1.6485.1001.2 STRING 0x1234                              <== event_code
        -v 1.3.6.1.4.1.6485.1001.3 STRING Warning                             <== severity
        -v 1.3.6.1.4.1.6485.1001.4 STRING This is test message              <== desc
        -v 1.3.6.1.4.1.6485.1001.5 STRING EMC                                 <== vendor
        -v 1.3.6.1.4.1.6485.1001.6 STRING STG                                  <== device_type
        -v 1.3.6.1.4.1.6485.1001.7 STRING realtime ssh                                  <== method
        -v 1.3.6.1.4.1.6485.1001.8 STRING etc                                  <== etc
        """
        
        errorIndication, errorStatus, errorIndex, varBinds = next(
            sendNotification(
                SnmpEngine(),
#                 CommunityData('public', mpModel=0),
#                 UsmUserData('usr-md5-none', 'authkey1'),
                UsmUserData('MD5DES', 'authkey1', 'privkey1'),
                UdpTransportTarget((snmp_ip, 162)),
                ContextData(),
                'trap',
                NotificationType(
                    ObjectIdentity('1.3.6.1.4.1.6485.901'),
                ).addVarBinds(
                    ('1.3.6.1.4.1.6485.1001.0', OctetString(errDic['serial'])),
                    ('1.3.6.1.4.1.6485.1001.1', OctetString(errDic['event_date'])),
                    ('1.3.6.1.4.1.6485.1001.2', OctetString(errDic['event_code'])),
                    ('1.3.6.1.4.1.6485.1001.3', OctetString(errDic['severity'])),
                    ('1.3.6.1.4.1.6485.1001.4', OctetString(errDic['desc'])),
                    ('1.3.6.1.4.1.6485.1001.5', OctetString(errDic['vendor'])),
                    ('1.3.6.1.4.1.6485.1001.6', OctetString(errDic['device_type'])),
                    ('1.3.6.1.4.1.6485.1001.7', OctetString(errDic['method'])),
                    ('1.3.6.1.4.1.6485.1001.8', OctetString(errDic['etc'])),
                    
                )
            )
        )
        if errorIndication:
            print(errorIndication)        
        
   
    def main(self):
        errDic={}
        errDic['serial']='11111'
        errDic['event_date']='2019-06-26 15:00:01'
        errDic['event_code']='0x1234'
        errDic['severity']='Warning'
        errDic['desc']='test'
        errDic['vendor']='VMware'
        errDic['device_type']='vCenter'
        errDic['method'] = 'snmp'
        errDic['etc'] ='test222222'
        print errDic
        self.errSnmpTrapSendV2(errDic)
        
        
        
                
                
if __name__=='__main__':
    Load().main()
    