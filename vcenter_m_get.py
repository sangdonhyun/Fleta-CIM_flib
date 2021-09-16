#-*- coding: utf-8 -*
import threading
import vcenter_by_pyvmomi
import ConfigParser
import os

# CounterThread
class CounterThread(threading.Thread):
    def __init__(self,vc_info):
        self.vc_info = vc_info
        threading.Thread.__init__(self, name='Timer Thread')

    # CounterThread가 실행하는 함수
    def run(self):
        vcenter_by_pyvmomi.VCenter(self.vc_info).main()


def get_vc_list():
    cfg = ConfigParser.RawConfigParser()
    cfg_file = os.path.join('config','list.cfg')
    cfg.read(cfg_file)
    hostList = []
    for sec in cfg.sections():
        host = {}
        host['name'] = sec
        for opt in cfg.options(sec):
            host[opt] = cfg.get(sec, opt)
        hostList.append(host)
    return hostList

if __name__ == '__main__':
    vc_list = get_vc_list()
    for vc_info  in vc_list:
        timerThread = CounterThread(vc_info)
        timerThread.start()
    mainThread = threading.currentThread()
    for thread in threading.enumerate():
        if thread is not mainThread:
            thread.join()

