from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import argparse
import atexit
import ssl

class host_perform():
    def __init__(self):
        self.si = self.get_si()

    def get_si(self):
        host = '121.170.193.209'
        # host=self.vcInfo['ip']
        user = 'administrator@vsphere.local'
        password = 'Kes2719!'


        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
            si = SmartConnect(host=host,
                              user=user,
                              pwd=password,
                              port=50000,
                              sslContext=context)
        if not si:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(Disconnect, si)

        return si

    def main(self):
        """
        ip=121.170.193.209
        username=administrator@vsphere.local
        password=Kes2719!
        port = 50000
        """


        content = self.si.RetrieveContent()

        hostid=content.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0]
        hardware=hostid.hardware
        cpuobj=hardware.cpuPkg[0]
        print 'The CPU vendor is %s and the model is %s'  %(cpuobj.vendor,cpuobj.description)
        systemInfo=hardware.systemInfo
        print 'The server hardware is %s %s' %(systemInfo.vendor,systemInfo.model)
        memoryInfo=hardware.memorySize
        print 'The memory size is %d GB' %((memoryInfo)/(1024*1024*1024))

        viewManager = content.viewManager
        view = viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        hosts = view.view
        view.Destroy()
        cluster = None

        obj_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                           [vim.StoragePod],
                                                           True)
        ds_cluster_list = obj_view.view
        obj_view.Destroy()
        print ds_cluster_list
        for ds_cluster in ds_cluster_list:
            print 'ds_cluster.name',ds_cluster.name
            datastores = ds_cluster.childEntity
            print("Datastores: ")
            for datastore in datastores:
                print(datastore.name)




if __name__ == '__main__':
    host_perform().main()