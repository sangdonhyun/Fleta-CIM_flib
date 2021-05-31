#-*- coding: utf-8 -*
'''
Created on 2019. 10. 10.

@author: Administrator
'''
import get_esx_state
import get_vm_state
import oraevent
import ConfigParser
import os
import fletaLog
class vmEvent():
    def __init__(self):
        self.log=fletaLog.flog()
    
    def getUsers(self):
        users={}
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','user.cfg')
        cfg.read(cfgFile)
        for sec in cfg.sections():
            users[sec] = cfg.get(sec,'tel')
        return users
    
    def main(self):
        ora_insert=oraevent.Event()
        users=self.getUsers()
        print users
        
        esx_events=get_esx_state.vm_Perform().main()
        
        for event_msg in esx_events:
            for user in users.keys():
                tel_no=users[user]
                try:
                    V_MSG_SEND_ID,V_REF_SEND_MSG_ID=ora_insert.setEvent(tel_no, event_msg)
                    ora_insert.selectQeury(V_MSG_SEND_ID,V_REF_SEND_MSG_ID)
                except:
                    pass
                self.log.error('sms send user :%s'%user)
                self.log.error('sms send tel no :%s'%tel_no)
                self.log.error(event_msg)
        
        vm_events = get_vm_state.VM().main()
        
        for event_msg in vm_events:
            for user in users.keys():
                tel_no=users[user]
                try:
                    V_MSG_SEND_ID,V_REF_SEND_MSG_ID=ora_insert.setEvent(tel_no, event_msg)
                    ora_insert.selectQeury(V_MSG_SEND_ID,V_REF_SEND_MSG_ID)
                except:
                    pass
                self.log.error('sms send user :%s'%user)
                self.log.error('sms send tel no :%s'%tel_no)
                self.log.error(event_msg)
                
    

if __name__=='__main__':
    vmEvent().main()