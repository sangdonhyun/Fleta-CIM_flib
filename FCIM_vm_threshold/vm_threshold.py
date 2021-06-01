'''
Created on 2020. 4. 26.

@author: user
'''
import os
import redis
import ConfigParser
import datetime
import event_threshold
import event_send_oracle
import fletaSnmp
import time

class vm_threshold():
    def __init__(self):
        self.cfg=self.get_cfg()
        self.redis = self.get_redis()
        self.ev_threshold=event_threshold.threshold()
        self.threshold_common=self.ev_threshold.common_threshold()
        self.threshold_each  = self.ev_threshold.each_threshold()
        self.vm_dict=self.ev_threshold.get_all_vname()
        self.uuid_set=self.threshold_each.keys()
        self.ora=event_send_oracle.vmEvent()
        self.snmp = fletaSnmp.Load()
        
        
    
    def get_common_threshold(self):
        cpu=self.threshold_common['cpu']
        mem=self.threshold_common['mem']
        disk=self.threshold_common['disk']
        return int(cpu),int(mem),int(disk)
    def get_cfg(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','Perform.cfg')
#         print cfgFile,os.path.isfile(cfgFile)
        cfg.read(cfgFile)
        return cfg
    
    def get_redis(self):
        redis_ip=self.cfg.get('redis','host')
        redis_port=self.cfg.get('redis','port')
        redis_passwd=self.cfg.get('redis','password')
        return redis.StrictRedis(host=redis_ip,port=int(redis_port),db=0,password=redis_passwd)  
    
    def set_event(self,vm_name,vc_name,dev,val,com_val):
        msg="[MXG SMS] vmware Server Alert:vm guest (vmname : {} {}) {} Threshold over {} (threshold {})".format(vm_name,vc_name,dev,val,com_val) 
        return msg
    
    def get_vm_name(self,uuid,ip):
        vm_uuid_set=self.vm_dict.keys()
        if uuid in vm_uuid_set:
            vm_name,vc_name=self.vm_dict[uuid]
        else:
            vm_name,vc_name ='unknown',ip
        return vm_name,vc_name
            
    
    
    def snmp_send(self,smsInfo):
        """
        smsInfo['vm_uuid']
        smsInfo['status_date']
        smsInfo['severity']
        smsInfo['desc']
        """
        errDic={}
        errDic['serial']=smsInfo['vm_uuid']
        errDic['event_date']=smsInfo['status_date']
        errDic['event_code']='vm-esx001'
        errDic['severity']=smsInfo['severity']
        errDic['desc']=smsInfo['desc']
        errDic['vendor']='VMware'
        errDic['device_type']='VCT'
        errDic['method'] = 'snmp'
        errDic['etc'] =str(smsInfo)
        
        try:
#             print errDic
            self.snmp.errSnmpTrapSend(errDic)
#             self.snmp.errSnmpTrapSendV3(errDic)
        except:
            pass
            # self.log.error('SNMP SEND ERROR')
            # self.log.error(str(errDic))
    
    def main(self):
        dt=datetime.datetime.now() - datetime.timedelta(minutes=1)
        dt_min=dt.strftime('%Y-%m-%d %H:%M')
        pt="{}*::VM perform real time::*".format(dt_min)
        keys = self.redis.keys(pt)
        print 'cnt :',len(keys)
        event_list=[]
        for key in keys:
            val= self.redis.get(key)

            date_time=key.split('::')[0]
            sp = val.split('^^')
            uuid=sp[0]
            ip = sp[1]
            cpu=sp[2]
            mem=sp[3]
            disk=sp[4]
            if uuid=='564d6edc-621b-b2b6-a056-01809a98f4fe':
                
                self.threshold_each[uuid]=['10','10','10']
                
                threshold_cpu,threshold_mem,threshold_disk=self.threshold_each[uuid]
                
                if int(float(cpu)) > int(threshold_cpu):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "CPU", cpu, threshold_cpu)
                    event_list.append([msg,date_time,uuid])
                    
                if int(float(mem)) > int(threshold_mem):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "MEMMORY", mem, threshold_mem)
                    event_list.append([msg,date_time,uuid])
                    
                if int(float(disk)) > int(threshold_disk):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "DISK", disk, threshold_disk)
                    event_list.append([msg,date_time,uuid])
                
            if uuid in self.uuid_set:
                
                threshold_cpu,threshold_mem,threshold_disk=self.threshold_each[uuid]
                
                if int(float(cpu)) > int(threshold_cpu):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "CPU", cpu, threshold_cpu)
                    event_list.append([msg,date_time,uuid])
                    
                if int(float(mem)) > int(threshold_mem):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "MEMMORY", cpu, threshold_mem)
                    event_list.append([msg,date_time,uuid])
                    
                if int(float(disk)) > int(threshold_disk):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "DISK", cpu, threshold_disk)
                    event_list.append([msg,date_time,uuid])
                    
            else:
                com_cpu,com_mem,com_disk=self.get_common_threshold()
                if int(float(cpu)) > com_cpu:
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "CPU", cpu, com_cpu)
                    event_list.append([msg,date_time,uuid])
                if int(float(mem)) > com_mem:
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "MEMMORY", cpu, com_cpu)
                    event_list.append([msg,date_time,uuid])
                    
                if int(float(disk)) > com_disk:
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "DISK", cpu, com_cpu)
                    event_list.append([msg,date_time,uuid])
        
        print 'event count :',len(event_list)
        for event_msg,date_time,uuid in event_list:
            print event_msg
            self.ora.send_event(event_msg)
            smsInfo ={}
            smsInfo['vm_uuid']=uuid
            smsInfo['status_date']=date_time
            smsInfo['desc']=event_msg
            smsInfo['severity'] = 'RED'
            print smsInfo['severity'] 
            self.snmp_send(smsInfo)
            
if __name__=="__main__":
    while True:
        vm_threshold().main()
        time.sleep(60)
            