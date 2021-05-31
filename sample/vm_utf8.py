#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author         : Eric Winn 
# @Email          : eng.eric.winn@gmail.com 
# @Time           : 2018/9/9 15:20
# @Version        : 1.0
# @File           : get_esxi_and_vm
# @Software       : PyCharm

import argparse
import atexit
import ssl
from pyVim import connect
from pyVmomi import vmodl,vim


def help_parser():
    """
    Builds a standard argument parser with arguments for talking to vCenter

    -s service_host_name_or_ip
    -o optional_port_number
    -u required_user
    -p optional_password

    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter or ESXi')

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=True,
                        action='store',
                        help='Password to use when connecting to host')

    return parser


def parse_service_instance(service_instance):
    '''
    :param service_instance:
    :return:
    '''
    content = service_instance.RetrieveContent()
    object_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [], True)

    for obj in object_view.view:
        if isinstance(obj, vim.ComputeResource):
            if isinstance(obj, vim.ClusterComputeResource):

                print('VcenterCluster: {}'.format(obj.name))

                for h in obj.host:
                    nic = h.config.network.vnic[0].spec
                    esxi_config = h.summary.config

                    print('''
                        ip:{}
                        mac:{}
                        os:{}
                        hostname:{}
                        '''.format(nic.ip.ipAddress, nic.mac, esxi_config.product.fullName, esxi_config.name))

                    for vx in h.vm:
                        if vx.summary.config.template is False:
                            for device in vx.config.hardware.device:
                                if (device.key >= 4000) and (device.key < 5000):
                                    print('''
                                    name:{}
                                    ip:{}
                                    cpu_cores:{}
                                    memory:{}
                                    mac:{}
                                    hostname:{}
                                    power_state:{}
                                    '''.format(vx.name,
                                               vx.summary.guest.ipAddress,
                                               vx.summary.config.numCpu,
                                               vx.summary.config.memorySizeMB,
                                               device.macAddress,
                                               vx.name,
                                               str(vx.summary.runtime.powerState),
                                               ))

            else:
                print('VcenterESXi: {}'.format(obj.name))
                for v in obj.host:
                    nic = v.config.network.vnic[0].spec
                    esxi_config = v.summary.config
                    print('''
                        ip:{}
                        mac:{}
                        os:{}
                        hostname:{}
                        '''.format(nic.ip.ipAddress, nic.mac, esxi_config.product.fullName, esxi_config.name))
                    for vx in v.vm:
                        if vx.summary.config.template is False:
                            for device in vx.config.hardware.device:
                                if (device.key >= 4000) and (device.key < 5000):
                                    print('''
                                    name:{}
                                    ip:{}
                                    cpu_cores:{}
                                    memory:{}
                                    mac:{}
                                    hostname:{}
                                    power_state:{}
                                    '''.format(vx.name,
                                               vx.summary.guest.ipAddress,
                                               vx.summary.config.numCpu,
                                               vx.summary.config.memorySizeMB,
                                               device.macAddress,
                                               vx.name,
                                               str(vx.summary.runtime.powerState),
                                               ))
                                    print vx.summary
                    object_view.Destroy()
                    return 0


def makeConnect():
    """
    :return:
    """
    host='10.10.10.64'
    user='administrator@vsphere.local'
    pwd='Kes2719!'
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE

        service_instance = connect.SmartConnect(
            host=host,
            user=user,
            pwd=pwd,
            port=443,
            sslContext=context
        )
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(connect.Disconnect, service_instance)

        # ## Do the actual parsing of data ## #
        parse_service_instance(service_instance)

    except vmodl.MethodFault as e:
        return -1
    return 0


if __name__ == '__main__':
    content = makeConnect()
    print(content)