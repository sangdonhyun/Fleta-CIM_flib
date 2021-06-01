'''
Created on 2019. 8. 5.

@author: user
'''
import ConfigParser
import os
from pysnmp.hlapi import *
print ("It worked!")

def send_snmp(errDic):
    """
    {'Category': 'Device(00BD4)', 'Src': 'Symm', 'Severity': 'Warning', 'symid': '000292603896', 'Descript': 'Access was attempted to a Not Ready device', 'ErrorNum': '0x003f', 'Time': '2018-06-25 10:15:50', 'Dir': 'FA-8G'}
    """
    cfg=ConfigParser.RawConfigParser()
    cfgFile='config\\config.cfg'
    cfg.read(cfgFile)
    print os.path.isfile(cfgFile)
    try:
        snmp_ip=cfg.get('server','snmp_ip')
    except:
        snmp_ip='localhost'
    
    print (snmp_ip)
    
    
    """
    -v 1.3.6.1.4.1.6485.901.0 STRING 1234567                            <== serial
    -v 1.3.6.1.4.1.6485.901.1 STRING 2019-02-26 02:02:01             <== event_date
    -v 1.3.6.1.4.1.6485.901.2 STRING 0x1234                              <== event_code
    -v 1.3.6.1.4.1.6485.901.3 STRING Warning                             <== severity
    -v 1.3.6.1.4.1.6485.901.4 STRING This is test message              <== desc
    -v 1.3.6.1.4.1.6485.901.5 STRING EMC                                 <== vendor
    -v 1.3.6.1.4.1.6485.901.6 STRING STG                                  <== device_type
    -v 1.3.6.1.4.1.6485.901.7 STRING realtime ssh                                  <== method
    -v 1.3.6.1.4.1.6485.901.8 STRING etc                                  <== etc
    """
    
    errorIndication, errorStatus, errorIndex, varBinds = next(
        sendNotification(
            SnmpEngine(),
            CommunityData('public', mpModel=0),
            UdpTransportTarget((snmp_ip, 162)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity('1.3.6.1.4.1.6485.901'),
            ).addVarBinds(
                ('1.3.6.1.4.1.6485.901.0', OctetString(errDic['symid'])),
                ('1.3.6.1.4.1.6485.901.1', OctetString(errDic['Time'])),
                ('1.3.6.1.4.1.6485.901.2', OctetString(errDic['ErrorNum'])),
                ('1.3.6.1.4.1.6485.901.3', OctetString(errDic['Severity'])),
                ('1.3.6.1.4.1.6485.901.4', OctetString(errDic['Descript'])),
                ('1.3.6.1.4.1.6485.901.5', OctetString('EMC')),
                ('1.3.6.1.4.1.6485.901.6', OctetString('STORAGE')),
                ('1.3.6.1.4.1.6485.901.7', OctetString('symevent')),
                ('1.3.6.1.4.1.6485.901.8', OctetString(errDic['Category'])),
                
            )
        )
    )
    if errorIndication:
        print(errorIndication)
raw_input('test')