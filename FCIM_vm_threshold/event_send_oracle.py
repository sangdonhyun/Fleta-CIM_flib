#-*- coding: utf-8 -*
'''
Created on 2019. 10. 10.

@author: Administrator
'''
import event_oracle
import ConfigParser
import os
import time
import datetime
import event_oracle
class vmEvent():
    def __init__(self):
        pass
        
    def getUsers(self):
        users={}
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','user.cfg')
        cfg.read(cfgFile)
        for sec in cfg.sections():
            users[sec] = cfg.get(sec,'tel')
        return users
    
    def get_user_by_db(self):
        pass
    
    def send_event(self,event_msg):
        users=self.getUsers()
        for user in users.keys():
            tel_no=users[user]
            try:
                V_MSG_SEND_ID,V_REF_SEND_MSG_ID=self.event_ora.setEvent(tel_no, event_msg)
                self.event_ora.selectQeury(V_MSG_SEND_ID,V_REF_SEND_MSG_ID)
            except:
                pass
    def send_event_list(self,event_list):
        users=self.getUsers()
        for event_msg in event_list:
            for user in users.keys():
                tel_no=users[user]
                try:
                    V_MSG_SEND_ID,V_REF_SEND_MSG_ID=self.event_ora.setEvent(tel_no, event_msg)
                    self.event_ora.selectQeury(V_MSG_SEND_ID,V_REF_SEND_MSG_ID)
                except:
                    pass        
    def main(self):
        pass
                

if __name__=='__main__':
    event_msg="[MXG SMS] {p$sid$} Server Alert: p$resource_name$ (p$string_level$:p$value$) p$description$"
    vmEvent(event_msg).main()

