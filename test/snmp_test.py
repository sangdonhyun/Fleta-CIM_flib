from pysnmp.hlapi import *

iterator = sendNotification(
    SnmpEngine(),
    CommunityData('public', mpModel=0),
    UdpTransportTarget(('localhost', 162)),
    ContextData(),
    'trap',
    NotificationType(
        ObjectIdentity('1.3.6.1.6.3.1.1.5.2')
    ).addVarBinds(
        ('1.3.6.1.6.3.1.1.4.3.0', '1.3.6.1.4.1.20408.4.1.1.2'),
        ('1.3.6.1.2.1.1.1.0', OctetString('my system2222'))
    ).loadMibs(
        'SNMPv2-MIB'
    )
)

errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

if errorIndication:
    print(errorIndication)