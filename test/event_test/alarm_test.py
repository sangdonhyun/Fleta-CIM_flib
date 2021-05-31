from __future__ import print_function
import os
import ssl
import sys
import requests

# This is where VMWare keeps the pyVmomi and other libraries
os.environ['VMWARE_PYTHON_PATH'] = 'C:\\python27'
sys.path.extend(os.environ['VMWARE_PYTHON_PATH'].split(';'))

from pyVim import connect
from pyVmomi import vim
requests.packages.urllib3.disable_warnings()
# this is to ignore SSL verification which is helpful for self signed certs
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
USER_NAME = "administrator@vsphere.local"
PASSWORD = "Kes2719!"
HOST = "10.10.10.64"
PORT = "443"
service_instance = connect.SmartConnect(host=HOST,
                                        user=USER_NAME,
                                        pwd=PASSWORD,
                                        port=int(PORT))

root_folder = service_instance.content.rootFolder
print (root_folder.name)
# again crude example here. use the logging module instead
with open("y_script_log_file.txt", 'a') as f:
    print(root_folder.name, file=f)
    for var, val in os.environ.items():
        # When an alarm is triggered and run a lot of environment variables are set. 
        # This will list them all with their values.
        if var.startswith("VMWARE_ALARM"):
            print("{} = {}".format(var, val), file=f)
    print("##########", file=f)
connect.Disconnect(service_instance)