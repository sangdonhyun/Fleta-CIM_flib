import pyVmomi
from pyVim.connect import SmartConnect
import ssl
host = '121.170.193.209'
user = 'administrator@vsphere.local'
pwd = 'Kes2719!'
port = 50000
context = None
si = SmartConnect(host=host,
                  user=user,
                  pwd=pwd,
                  port=port)
print 'si :',si