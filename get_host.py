'''
Created on 2019. 9. 24.

@author: Administrator
'''
import subprocess

from pyVim import connect

# proc = subprocess.Popen(["sudo dmidecode|grep UUID|awk '{print $2}'"], stdout=subprocess.PIPE, shell=True)
# (out, err) = proc.communicate()
uuid = '564d2cce-709a-c62f-3b13-a4e841ab5c60'

SI = None
SI = connect.SmartConnect(host='10.10.10.64',
                          user='administrator@vsphere.local',
                          pwd='Kes2719!',
                          port=443)

VM = SI.content.searchIndex.FindByUuid(None, uuid,
                                       True,
                                       False)

HOST = VM.runtime.host

print "Host name: {}".format(HOST.name)