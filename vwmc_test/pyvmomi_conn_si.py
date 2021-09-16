import ssl
import pyVim
from pyVim.connect import SmartConnect, Disconnect,SmartConnectNoSSL
from pyVmomi import vim, vmodl
import requests
context = None

# Disabling urllib3 ssl warnings
# requests.packages.urllib3.disable_warnings()

# Disabling SSL certificate verification


vc = None
"""
[vcenter1]
ip=121.170.193.209
username=administrator@vsphere.local
#username=VSPHERE.LOCAL/Administrator
password=Kes2719!
#port = 443
port = 50000

"""
vcenter_host = "121.170.193.209"
vcenter_port = 50000
vcenter_username = "administrator@vsphere.local"
vcenter_password = "Kes2719!"

# Connecting to vCenter
try:

    # si = pyVim.connect.Connect(host=vcenter_host, user=vcenter_username, pwd=vcenter_password, port=vcenter_port)
    # context = ssl._create_unverified_context()
    # si = SmartConnect(host=vcenter_host, user=vcenter_username, pwd=vcenter_password, port=vcenter_port,sslContext=context)
    si = SmartConnectNoSSL(host=vcenter_host, user=vcenter_username, pwd=vcenter_password, port=vcenter_port)
    print (dir(si))

    aboutInfo = si.content.about
    print dir(aboutInfo)
    print ("Product Name    :", aboutInfo.fullName)
    print("Product Build    :", aboutInfo.build)
    print("Product Unique Id:", aboutInfo.instanceUuid)
    print("Product Version  :", aboutInfo.version)
    print("Product Base OS  :", aboutInfo.osType)
    print("Product vendor   :", aboutInfo.vendor)

except IOError as e:
    print str(e)


# Do stuff