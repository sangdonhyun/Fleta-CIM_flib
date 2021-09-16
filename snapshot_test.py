from pyVmomi import vim

from pyVim.connect import SmartConnectNoSSL, Disconnect

import argparse
import atexit
import getpass
import json
import ConfigParser
import os

"""
        Iterate through all datacenters and list VM info.
        [vcenter1]
ip=121.170.193.209
username=administrator@vsphere.local
password=Kes2719!
port = 50000
        """
vc_ip = '121.170.193.209'
user = 'administrator@vsphere.local'
passwd = 'Kes2719!'
port = 50000

vmstatList = []
vmSMSList = []
data = dict()
si = SmartConnectNoSSL(host=vc_ip,
                       user=user,
                       pwd=passwd,
                       port=int(port))
if not si:
    print("Could not connect to the specified host using specified "
          "username and password")


atexit.register(Disconnect, si)

content = si.RetrieveContent()
content = si.content
objView = content.viewManager.CreateContainerView(content.rootFolder,
                                                [vim.VirtualMachine],
                                                True)
vmList = objView.view
objView.Destroy()
"""
['AcquireMksTicket', 'AcquireTicket', 'Answer', 'AnswerVM', 'ApplyEvcMode', 'ApplyEvcModeVM_Task', 'Array', 'AttachDisk', 'AttachDisk_Task', 'CheckCustomizationSpec', 'Clone', 'CloneVM_Task', 'ConsolidateDisks', 'ConsolidateVMDisks_Task', 'CreateScreenshot', 'CreateScreenshot_Task', 'CreateSecondary', 'CreateSecondaryEx', 'CreateSecondaryVMEx_Task', 'CreateSecondaryVM_Task', 'CreateSnapshot', 'CreateSnapshotEx', 'CreateSnapshotEx_Task', 'CreateSnapshot_Task', 'CryptoUnlock', 'CryptoUnlock_Task', 'Customize', 'CustomizeVM_Task', 'DefragmentAllDisks', 'Destroy', 'Destroy_Task', 'DetachDisk', 'DetachDisk_Task', 'DisableSecondary', 'DisableSecondaryVM_Task', 'DropConnections', 'EnableSecondary', 'EnableSecondaryVM_Task', 'EstimateStorageForConsolidateSnapshots_Task', 'EstimateStorageRequirementForConsolidate', 'ExportVm', 'ExtractOvfEnvironment', 'InstantClone', 'InstantClone_Task', 'MakePrimary', 'MakePrimaryVM_Task', 'MarkAsTemplate', 'MarkAsVirtualMachine', 'Migrate', 'MigrateVM_Task', 'MountToolsInstaller', 'PowerOff', 'PowerOffVM_Task', 'PowerOn', 'PowerOnVM_Task', 'PromoteDisks', 'PromoteDisks_Task', 'PutUsbScanCodes', 'QueryChangedDiskAreas', 'QueryConnections', 'QueryFaultToleranceCompatibility', 'QueryFaultToleranceCompatibilityEx', 'QueryUnownedFiles', 'RebootGuest', 'ReconfigVM_Task', 'Reconfigure', 'RefreshStorageInfo', 'Reload', 'ReloadFromPath', 'Relocate', 'RelocateVM_Task', 'RemoveAllSnapshots', 'RemoveAllSnapshots_Task', 'Rename', 'Rename_Task', 'Reset', 'ResetGuestInformation', 'ResetVM_Task', 'RevertToCurrentSnapshot', 'RevertToCurrentSnapshot_Task', 'SendNMI', 'SetCustomValue', 'SetDisplayTopology', 'SetScreenResolution', 'ShutdownGuest', 'StandbyGuest', 'StartRecording', 'StartRecording_Task', 'StartReplaying', 'StartReplaying_Task', 'StopRecording', 'StopRecording_Task', 'StopReplaying', 'StopReplaying_Task', 'Suspend', 'SuspendVM_Task', 'Terminate', 'TerminateFaultTolerantVM', 'TerminateFaultTolerantVM_Task', 'TerminateVM', 'TurnOffFaultTolerance', 'TurnOffFaultToleranceForVM_Task', 'UnmountToolsInstaller', 'Unregister', 'UnregisterVM', 'UpgradeTools', 'UpgradeTools_Task', 'UpgradeVM_Task', 'UpgradeVirtualHardware', '_GetMethodInfo', '_GetMethodList', '_GetMoId', '_GetPropertyInfo', '_GetPropertyList', '_GetServerGuid', '_GetStub', '_InvokeAccessor', '_InvokeMethod', '__class__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_methodInfo', '_moId', '_propInfo', '_propList', '_serverGuid', '_stub', '_version', '_wsdlName', 'alarmActionsEnabled', 'availableField', 'capability', 'config', 'configIssue', 'configStatus', 'customValue', 'datastore', 'declaredAlarmState', 'disabledMethod', 'effectiveRole', 'environmentBrowser', 'guest', 'guestHeartbeatStatus', 'layout', 'layoutEx', 'name', 'network', 'overallStatus', 'parent', 'parentVApp', 'permission', 'recentTask', 'reloadVirtualMachineFromPath_Task', 'resourceConfig', 'resourcePool', 'rootSnapshot', 'runtime', 'setCustomValue', 'snapshot', 'storage', 'summary', 'tag', 'triggeredAlarmState', 'value']
"""
for vm in vmList:
    print vm
    print '-'*50
    print vm.summary.vm
    # print '='*50
    # print vm.snapshot
