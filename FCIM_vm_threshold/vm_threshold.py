'''
Created on 2020. 4. 26.

@author: user
'''
import os
import redis
import configparser
import datetime
import event_threshold
import event_send_oracle
import fletaSnmp
import time
import fletaDbms

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
        self.db = fletaDbms.FletaDb()

        print 'uuid set :',self.uuid_set
        
    
    def get_common_threshold(self):
        cpu=self.threshold_common['cpu']
        mem=self.threshold_common['mem']
        disk=self.threshold_common['disk']
        return int(cpu),int(mem),int(disk)
    def get_cfg(self):
        cfg=configparser.RawConfigParser()
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
            
    def get_today_th_list(self):
        query  ="SELECT serial_number ,tmp FROM EVENT.event_log el  WHERE event_code = 'vm-esx001' AND to_char(log_date,'YYYY-MM-DD') = to_char(now(),'YYYY-MM-DD')"
        td_list=self.db.getRaw(query)
        vm_list = list()
        for td in td_list:
            vm_list.append([td[0],td[1][0]])
        return vm_list

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
        errDic['etc'] = smsInfo['etc']
        
        try:
            print errDic
            self.snmp.errSnmpTrapSend(errDic)
        except Exception as e:
            print str(e)

    
    def main(self):
        dt=datetime.datetime.now() - datetime.timedelta(minutes=1)
        dt_min=dt.strftime('%Y-%m-%d %H:%M')
        pt="{}*::VM perform real time::*".format(dt_min)
        print pt
        keys = self.redis.keys(pt)
        print 'cnt :',len(keys)
        event_list=[]
        for key in keys:
            val= self.redis.get(key)
            print 'redis val :',val
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
                    event_list.append([msg,date_time,uuid,'CPU'])
                    
                if int(float(mem)) > int(threshold_mem):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "MEMMORY", mem, threshold_mem)
                    event_list.append([msg,date_time,uuid,'MEMORY'])
                    
                if int(float(disk)) > int(threshold_disk):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "DISK", disk, threshold_disk)
                    event_list.append([msg,date_time,uuid,'DISK'])
                
            if uuid in self.uuid_set:
                
                threshold_cpu,threshold_mem,threshold_disk=self.threshold_each[uuid]
                
                if int(float(cpu)) > int(threshold_cpu):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "CPU", cpu, threshold_cpu)
                    event_list.append([msg,date_time,uuid,'CPU'])
                    
                if int(float(mem)) > int(threshold_mem):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "MEMMORY", cpu, threshold_mem)
                    event_list.append([msg,date_time,uuid,'MEMORY'])
                    
                if int(float(disk)) > int(threshold_disk):
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "DISK", cpu, threshold_disk)
                    event_list.append([msg,date_time,uuid,'DISK'])
                    
            else:
                com_cpu,com_mem,com_disk=self.get_common_threshold()
                if int(float(cpu)) > com_cpu:
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "CPU", cpu, com_cpu)
                    event_list.append([msg,date_time,uuid,'CPU'])
                if int(float(mem)) > com_mem:
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "MEMMORY", cpu, com_cpu)

                    event_list.append([msg,date_time,uuid,'MEMORY'])

                if int(float(disk)) > com_disk:
                    ev_time= key.split('::')[0]
                    vm_name,vc_name= self.get_vm_name(uuid, ip)
                    msg=self.set_event(vm_name, vc_name, "DISK", cpu, com_cpu)
                    event_list.append([msg,date_time,uuid,'DISK'])
        
        print 'event count :',len(event_list)
        vm_today_list = self.get_today_th_list()

        for event_msg,date_time,uuid,etc in event_list:


            if [uuid,etc] in vm_today_list:
                    print 'alleady send in today'
            else:
                smsInfo = {}
                smsInfo['vm_uuid'] = uuid
                smsInfo['status_date'] = date_time
                smsInfo['desc'] = event_msg
                smsInfo['severity'] = 'RED'
                smsInfo['etc'] = etc
                self.snmp_send(smsInfo)
                self.ora.send_event(event_msg)

            
if __name__=="__main__":
    vm_threshold().main()
    # while True:
    #     vm_threshold().main()
    #     time.sleep(60)
            