#!/usr/bin/env python
#
# Written by JM Lopez
# GitHub: https://github.com/jm66
# Email: jm@jmll.me
# Website: http://jose-manuel.me
#
# Note: Example code For testing purposes only
#
# This code has been released under the terms of the Apache-2.0 license
# http://opensource.org/licenses/Apache-2.0
#

import atexit
import requests
from tools import cli
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import ssl
# disable  urllib3 warnings
if hasattr(requests.packages.urllib3, 'disable_warnings'):
    requests.packages.urllib3.disable_warnings()


def get_args():
    parser = cli.build_arg_parser()
    parser.add_argument('-n', '--name', required=False,
                        help="Name of the Datastore.")
    my_args = parser.parse_args()
    return cli.prompt_for_password(my_args)


def get_obj(content, vim_type, name=None):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vim_type, True)
    if name:
        for c in container.view:
            if c.name == name:
                obj = c
                return [obj]
    else:
        return container.view


# http://stackoverflow.com/questions/1094841/
def sizeof_fmt(num):
    """
    Returns the human readable version of a file size

    :param num:
    :return:
    """
    for item in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, item)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def print_datastore_info(ds_obj):
    summary = ds_obj.summary
    ds_capacity = summary.capacity
    ds_freespace = summary.freeSpace
    ds_uncommitted = summary.uncommitted if summary.uncommitted else 0
    ds_provisioned = ds_capacity - ds_freespace + ds_uncommitted
    ds_overp = ds_provisioned - ds_capacity
    ds_overp_pct = (ds_overp * 100) / ds_capacity \
        if ds_capacity else 0
    print ""
    print "Name                  : {}".format(summary.name)
    print "URL                   : {}".format(summary.url)
    print "Capacity              : {} GB".format(sizeof_fmt(ds_capacity))
    print "Free Space            : {} GB".format(sizeof_fmt(ds_freespace))
    print "Uncommitted           : {} GB".format(sizeof_fmt(ds_uncommitted))
    print "Provisioned           : {} GB".format(sizeof_fmt(ds_provisioned))
    if ds_overp > 0:
        print "Over-provisioned      : {} GB / {} %".format(
            sizeof_fmt(ds_overp),
            ds_overp_pct)
    print "Hosts                 : {}".format(len(ds_obj.host))
    print "Virtual Machines      : {}".format(len(ds_obj.vm))
    print summary

def main():
    host='10.10.10.64'
    user='administrator@vsphere.local'
    password='Kes2719!'
    
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
        si = SmartConnect(host=host,
                      user=user,
                      pwd=password,
                      sslContext=context)
    
    
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()
    
    # Get list of ds mo
    ds_obj_list = get_obj(content, [vim.Datastore])
    for ds in ds_obj_list:
        print_datastore_info(ds)

# start
if __name__ == "__main__":
    main()
