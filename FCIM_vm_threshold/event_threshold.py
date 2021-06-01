'''
Created on 2020. 4. 25.

@author: user
'''
import ConfigParser
import os
import sys
import psycopg2
from _sqlite3 import Row

class threshold():
    def __init__(self):
        self.cfg=self.get_cfg()
        self.conn_string = self.getConnStr()
    
    def get_cfg(self):
        cfg=ConfigParser.RawConfigParser()
        cfg_file = os.path.join('config','RDBload.cfg')
        cfg.read(cfg_file)
        return cfg
    
    
    def get_threshold_rows(self,query):
        con = None
        try:
            print self.conn_string
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            print query
            cur.execute(query)
            
            rows = cur.fetchall()
            
            if rows == None:
                self.com.sysOut('Empty result set from query')
            cur.close()
            con.close()
#             con.commit()
#             print "Number of rows updated: %d" % cur.rowcount
        except psycopg2.DatabaseError, e:
            if con:
                con.rollback()
            print 'Error %s' % e    
            sys.exit(1)
        finally:
            if con:
                con.close()
        return rows
    
    
    def getConnStr(self):
        ip=self.cfg.get('database','ip')
        dbname=self.cfg.get('database','dbname')
        user=self.cfg.get('database','user')
        passwd=self.cfg.get('database','passwd')
        return "host='%s' dbname='%s' user='%s' password='%s'"%(ip,dbname,user,passwd) 
    
    def get_user_by_db(self):
        query=""
    
    def each_threshold(self):
        query="""SELECT event_id, event_level, vendor_name, model_name, setting_value, 
       enable, serial
  FROM ref.ref_event_op_setting_value where event_id = 28
  
    """
        rows=self.get_threshold_rows(query)
        each_threshold_dict={}
        for row in rows:
            uuid= row[6]
            cpu = self.ptos(row[4][0])
            mem = self.ptos(row[4][1])
            disk = self.ptos(row[4][2])
            each_threshold_dict[uuid] = [cpu,mem,disk]
        return each_threshold_dict
    
    def ptos(self,str):
        if '%' in str:
            str=str.replace('%','')
        return str
    
    def common_threshold(self):
        query="""SELECT event_id, event_level, vendor_name, model_name, setting_value, 
       enable, serial
  FROM ref.ref_event_op_setting_value where event_id in (25,26,27)"""
        
        cpu_val,memory_val,disk_val = '','',''
        rows=self.get_threshold_rows(query)
        print query
        print rows
        for row in  rows:
            print row
            id=row[0]
            val=row[4][0]
            
            if id ==25:
                cpu_val=val
            if id ==26:
                memmory_val=val
            if id ==27:
                disk_val=val
        common_threshold={}
        common_threshold['cpu'] = self.ptos(cpu_val)
        common_threshold['mem'] = self.ptos(memmory_val)
        common_threshold['disk'] = self.ptos(disk_val)
        return common_threshold
    def get_htreshold(self):
        common_threshold=self.common_threshold()
        each_threshold=self.each_threshold()
        return common_threshold,each_threshold
    def get_vname(self,uuid):
        query="""
        SELECT v_center,  name
  FROM master.master_vm_info where uuid = '{}' """.format(uuid)
        rows=self.get_threshold_rows(query)
        if len(rows) > 0:
            vc_name=rows[0][0]
            vm_name=rows[0][1]
        else:
            vc_name=''
            vm_name=''
        return vc_name,vm_name
    
    
    def get_all_vname(self):
        query=""" SELECT v_center,  name,uuid FROM master.master_vm_info """
        vm_dict={}
        rows=self.get_threshold_rows(query)
        for row in rows:
            vc_name=row[0]
            vm_name=row[1]
            uuid = row[2]
            vm_dict[uuid]=[vc_name,vm_name]
        return vm_dict
    
    def main(self):
        com_thres,each_thres=self.get_htreshold()
        print com_thres
        print each_thres
        
if __name__=='__main__':
    threshold().main()