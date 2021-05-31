'''
Created on 2019. 7. 9.

@author: Administrator
'''

import atexit
from pyVim import connect
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi.VmomiSupport import Object, DataObject, F_LINK, F_LINKABLE, F_OPTIONAL, F_SECRET, ManagedObject
from pyVmomi.VmomiSupport import UncallableManagedMethod, ManagedMethod, binary, Iso8601
from pyVmomi import vmodl
from pyVmomi import vim
import base64
import json
import codecs
import sys
import chardet
import re
import datetime

class VM():
    def __init__(self,vmInfo):
        self.host = vmInfo['ip']
        self.user = vmInfo['username']
        self.passwd=vmInfo['password']

    def main(self):
        pass


if __name__ == "__main__":
    vmInfo={}
    vmInfo['ip'] = '10.10.10.64'
    vmInfo['username'] = 'administrator@vsphere.local'
    vmInfo['password'] = 'Kes2719!'
    VM(vmInfo).main()