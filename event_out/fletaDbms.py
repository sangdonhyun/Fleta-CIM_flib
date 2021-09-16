# -*- encoding:cp949*-    
'''
Created on 2013. 2. 11.

@author: Administrator
'''

import sys
import os
import psycopg2
import ConfigParser
import codecs
import locale

import datetime
import json



class FletaDb():
    def __init__(self):
#         self.logger = self.com.flog()
                
#         self.conn_string = "host='localhost' dbname='fleta' user='fletaAdmin' password='kes2719!'"
        self.conn_string = self.getConnStr()

        self.cfg = self.getCfg()
        
        
    
    def getCfg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def getConnStr(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        try:
            ip = cfg.get('database','ip')
        except:
            ip = 'localhost'
        try:
            user = cfg.get('database','user')
        except:
            user = 'webuser'
        try:
            dbname = cfg.get('database','dbname')
        except:
            dbname = 'fleta'
        try: 
            passwd = cfg.get('database','passwd')
        except:
            passwd = 'qw19850802@'

        return "host='%s' dbname='%s' user='%s' password='%s'"%(ip,dbname,user,passwd)
        
    
    def getConnectInfo(self):
        dbinfo = {}
        for info in self.cfg.options('database'):
            val = self.cfg.get('database',info)
            if (info == 'passwd' or info == 'user') and len(val) >20:
                val - self.dec.fdec(val)
            dbinfo[info] = val
        return dbinfo
    
    
    
    def queryExec(self,query):
        con = None
#         try:
        con = psycopg2.connect(self.conn_string)
        cur = con.cursor()
        
        cur.execute(query)
        con.commit()
#             print "Number of rows updated: %d" % cur.rowcount
#         except psycopg2.DatabaseError, e:
#             if con:
#                 con.rollback()
#             print 'Error %s' % e    
#             sys.exit(1)
#         finally:
#             if con:
#                 con.close()

    

    def isEvnt(self,query):
    
        db=psycopg2.connect(self.conn_string)
        cursor = db.cursor()
        print 'query 2:',query
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if rows == None:
            print 'none'
        
                
        cursor.close()
        db.close()
        return rows[0]
    
    def evtInsert(self,insquery):
        con = None
        try:
             
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            
            cur.execute(insquery)
            con.commit()
            
#             print "Number of rows updated: %d" % cur.rowcount
               
        
        except psycopg2.DatabaseError, e:
            
            if con:
                con.rollback()
            
            print 'Error %s' % e    
            sys.exit(1)
            
            
        finally:
            
            if con:
                con.close()

    def qwrite(self,msg,wbit='a'):
        with open('query.txt',wbit) as f:
            f.write(msg+'굍굈')
    
    def isilonQuery(self,dic,table='monotir.pm_auto_isilon_info'):
        colList= dic.keys()
        valList= dic.values()
        colStr = '('
        for i in colList:
            colStr += "%s"%i +','
        if colStr[-1]==',':
            colStr = colStr[:-1]+')'
        val = ()
        for i in valList:
            
            val+=(i,)
        valStr = str(val)
        query = 'insert into %s %s values %s;'%(table,colStr,valStr)
#         print query
        return query
        
    def listInsert(self,dicList,table='monitor.perform_stg_avg'):
        qList=[]
        for dic in dicList:
            colList= dic.keys()
            valList= dic.values()
            colStr = '('
            for i in colList:
                colStr += "%s"%i +','
            if colStr[-1]==',':
                colStr = colStr[:-1]+')'
            val = ()
            for i in valList:
                
                val+=(i,)
            valStr = str(val)
            query = 'insert into %s %s values %s;'%(table,colStr,valStr)
            
            try:
                con = psycopg2.connect(self.conn_string)
                cur = con.cursor()
                cur.execute(query)
                con.commit()
            except psycopg2.DatabaseError, e:
                if con:
                    con.rollback()
                print 'Error %s' % e    
                sys.exit(1)
            finally:
                if con:
                    con.close()
            qList.append(query)
        return qList
    def dicInsert(self,dic,table='monitor.perform_stg_avg'):
        
        
        colList= dic.keys()
        valList= dic.values()
        colStr = '('
        for i in colList:
            colStr += "%s"%i +','
        if colStr[-1]==',':
            colStr = colStr[:-1]+')'
        val = ()
        for i in valList:
            
            val+=(i,)
        valStr = str(val)
        query = 'insert into %s %s values %s;'%(table,colStr,valStr)
        print query
        try:
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            cur.execute(query)
            con.commit()
        except psycopg2.DatabaseError, e:
            if con:
                con.rollback()
            print 'Error %s' % e    
#             sys.exit(1)
        finally:
            if con:
                con.close()
    
    
    
    def getQList(self,dicList,table='monitor.perform_stg_avg'):
        qList=[]
        for dic in dicList:
            colList= dic.keys()
            valList= dic.values()
            colStr = '('
            for i in colList:
                colStr += "%s"%i +','
            if colStr[-1]==',':
                colStr = colStr[:-1]+')'
            val = ()
            for i in valList:
                
                val+=(i,)
            valStr = str(val)
            query = 'insert into %s %s values %s;'%(table,colStr,valStr)
            qList.append(query)
        return qList
#         print query
    
    
    def dbInsertDicList(self,dicList,table='monotir.pm_auto_isilon_info'):
        qList=self.getQList(dicList, table)
        con = None
        
        
        
        try:
              
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            for q in qList:
                
                cur.execute(q)
            con.commit()
             
#             print "Number of rows updated: %d" % cur.rowcount
                
         
        except psycopg2.DatabaseError, e:
             
            if con:
                con.rollback()
             
            print 'Error %s' % e    
            sys.exit(1)
             
             
        finally:
             
            if con:
                con.close()
        
            
    
    
    def dbInsert(self,dic,table='monotir.perform_stg_avg'):
        
        colList= dic.keys()
        valList= dic.values()
        colStr = '('
        for i in colList:
            colStr += "%s"%i +','
        if colStr[-1]==',':
            colStr = colStr[:-1]+')'
        val = ()
        for i in valList:
            
            val+=(i,)
        valStr = str(val)
        query = 'insert into %s %s values %s;'%(table,colStr,valStr)
#         print query
        self.qwrite(query)
        con = None
         
        try:
              
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
#                         
            cur.execute(query)
            con.commit()
             
#             print "Number of rows updated: %d" % cur.rowcount
                
         
        except psycopg2.DatabaseError, e:
             
            if con:
                con.rollback()
             
            print 'Error %s' % e    
            sys.exit(1)
             
             
        finally:
             
            if con:
                con.close()
    
    def dbQeuryIns(self,query):
        con = None
        try:
             
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            cur.execute(query)
            con.commit()
        except psycopg2.DatabaseError, e:
            
            if con:
                con.rollback()
            
            print 'Error %s' % e    
#             sys.exit(1)
        finally:
            
            if con:
                con.close()

    
    
    
    def eventList(self):
        db=psycopg2.connect(self.conn_string)
        cursor = db.cursor()
        
        query_string = self.getQuery()
        cursor.execute(query_string)
        rows = cursor.fetchall()
        
        if rows == None:
            self.com.sysOut('Empty result set from query')
        
                
        cursor.close()
        db.close()
        return rows
    
    def getRaw(self,query_string):
        db=psycopg2.connect(self.conn_string)
        
        try:
            cursor = db.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchall()
        
            
            cursor.close()
            db.close()
            
            return rows
        except:
            return []
    
    
    
    def isEvtByQeury(self,query):
       
       
        conn = None
        try:
             
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
            
        except:
            print "I am unable to connect to the database."
        
        # If we are accessing the rows via column name instead of position we 
        # need to add the arguments to conn.cursor.
        
#         cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            cur.execute(query)
        except:
            pass
        #
        # Note that below we are accessing the row via the column name.
        try:
            rows = cur.fetchall()
    
            if rows[0][0] == 0:
                return True
            else:
                return False
        except:
            pass
    def getEvent(self):
        tday=datetime.datetime.now().strftime('%Y-%m-%d')
        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
        except:
            print "I am unable to connect to the database."
        query="""SELECT seq_no, log_date, check_date, event_date, serial_number, event_code, 
       event_level, q_event_level, desc_summary, desc_detail, device_type, 
       vendor_name, event_method, action_date, action_contents, user_id, 
       category_a, category_b, category_c, tmp
  FROM event.event_log where log_date='%s'"""%tday
        try:
            cur.execute(query)
        except:
            pass
        #
        # Note that below we are accessing the row via the column name.
        try:
            rows = cur.fetchall()
            
        except:
            pass
        
        return rows
    
    def set_guest_status(self):
        j_dict = {}

        i = 0
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()

        except Exception as e:
            print str(e)
            print "unable to connect to the database."

        query = "SELECT * FROM vnstatus.vnstatus_guest_status;"
        cur.execute(query)
        try:
            for row in cur:
                j_dict[i] = {'ip': row[0], 'Loc': row[1]}
                i = i + 1

            with open(os.path.join('config','guest_status.txt'), 'w', encoding='utf-8') as file:
                json.dump(j_dict, file, indent=4)
        except Exception as e:
            print str(e)
        conn.close()

    def getList(self,obj):
        conn = None
        rows = []
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
        except:
            print "I am unable to connect to the database."
        query="SELECT * FROM vnstatus.vnstatus_%s_status;"%obj

        try:
            cur.execute(query)
        except:
            pass
        #
        # Note that below we are accessing the row via the column name.
        try:
            rows = cur.fetchall()
            if len(rows) == 0:
                rows = None
        except:
            pass
        
        return rows
    
    
    def esx_upsert(self,esxDicList):
        con = None
        
        con = psycopg2.connect(self.conn_string)
        cur = con.cursor()
        for esxDic in esxDicList:
            """
            {'esx_uuid': '238c3fe4-3a77-11e2-81e9-6cae8b62d8d2', 'vc_vcenter': '121.170.193.209', 'ping_status': 'False', 'status_date': '2021-05-28 17:09:48', 'esx_ip': '10.10.10.10'}
            """

            uuid = esxDic['esx_uuid']
            status_date=esxDic['status_date']
            esx_ip = esxDic['esx_ip']
            ping_status=esxDic['ping_status']
            vc_vcenter = esxDic['vc_vcenter']
            # print esxDic

            uuid = esxDic['esx_uuid']
            query="""
            INSERT INTO vnstatus.vnstatus_esx_status
(status_date, uuid, esx_ip, health_type, health_name, health_status, vc_vcenter)
VALUES('{DATE}', '{UUID}', '{ESX_IP}','PING_STATUS', 'PING_STATUS','{PING_STATUS}', '{VCENTER}');
           
            """.format(DATE=status_date,UUID=uuid,ESX_IP=esx_ip,PING_STATUS=ping_status,VCENTER=vc_vcenter)
            # print query
            cur.execute(query)
        con.commit()
        
    def conn_test(self):
        con = None
        try:
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            query='select count(*) from vnstatus.vnstatus_guest_status'
            cur.execute(query)
            cnt = cur.fetchone()
            cur.close()
        except psycopg2.DatabaseError, e:
            if con:
                con.rollback()
            print 'Error %s' % e    
#             sys.exit(1)
        finally:
            if con:
                con.close()
    def upsert(self,vmDicList):
    
        con = None
        try:
             
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            for vmDic in vmDicList:
                
                status_date=vmDic['status_date']
                vm_uuid=vmDic['vm_uuid']
                vm_ip=vmDic['vm_ip']
                vm_name=vmDic['vm_name']
                vm_hostname=vmDic['vm_hostname']
                vm_power=vmDic['vm_power']
                vc_vcenter=vmDic['vc_vcenter']
                vc_hostserver=vmDic['vc_hostserver']
                query="""
                INSERT INTO vnstatus.vnstatus_guest_status
                (status_date,vm_uuid,vm_ip,vm_name,vm_hostname,vm_power,vc_vcenter,vc_hostserver) values (
                '%s',
                '%s',
                '%s',
                '%s',
                '%s',
                '%s',
                '%s',
                '%s')
                """%(status_date,vm_uuid,vm_ip,vm_name,vm_hostname,vm_power,vc_vcenter,vc_hostserver)
                # print query
                cur.execute(query)
            con.commit()
        except psycopg2.DatabaseError, e:
            
            if con:
                con.rollback()
            
            print 'Error %s' % e    
#             sys.exit(1)
        finally:
            
            if con:
                con.close()



if __name__ == '__main__':
    """
    2019-05-15 13:15:40::4200454a-71cf-e743-a780-0032abccf0ad::W_2016_restapi_68::cpu::usage average 29.0
    """
    vmDic={}
    vmDic['status_date']='2019-10-08 19:35:15'
    vmDic['vm_uuid']='564ddfe5-e56f-b340-f03d-7e8f8378e32c'
    vmDic['vm_ip']='10.10.10.59'
    vmDic['vm_name']='Linux_Redhat6.7_59'
    vmDic['vm_hostname']='Redhat6_59'
    vmDic['vm_power']='poweredOn'
    vmDic['vcenter']='10.10.10.64'
    vmDic['vc_hostserver']='10.10.10.11'
    query='''
     INSERT INTO vnstatus.vnstatus_guest_status
        (status_date,vm_uuid,vm_ip,vm_name,vm_hostname,vm_power,vc_vcneter,vc_hostserver) values (
        '2019-10-08 19:35:15',
        '564ddfe5-e56f-b340-f03d-7e8f8378e32c',
        '10.10.10.59',
        'Linux_Redhat6.7_59',
        'Redhat6_59',
        'poweredOn',
        '10.10.10.64',
        '10.10.10.11')
    '''
    vmDicList=[]
    vmDicList.append(vmDic)
    print FletaDb().upsert(vmDicList)
        