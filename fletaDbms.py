# -*- encoding:cp949*-    
'''
Created on 2013. 2. 11.

@author: Administrator
'''

import sys
import os
import psycopg2
import configparser
import codecs
import locale
import common




class FletaDb():
    def __init__(self):
        self.com = common.Common()
        self.dec = common.Decode()
#         self.logger = self.com.flog()
                
#         self.conn_string = "host='localhost' dbname='fleta' user='fletaAdmin' password='kes2719!'"
        self.conn_string = self.getConnStr()
        print(self.conn_string)
        self.cfg = self.getCfg()
        
        
    
    def getCfg(self):
        cfg = configparser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def getConnStr(self):
        cfg = configparser.RawConfigParser()
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
        
        
        if len(passwd)>20:
            try:
                passwd= self.dec.fdec(passwd)
            except:
                pass
        
        return "host='%s' dbname='%s' user='%s' password='%s'"%(ip,dbname,user,passwd)
        
    
    def getConnectInfo(self):
        dbinfo = {}
        for info in self.cfg.options('database'):
            val = self.cfg.get('database',info)
            if (info == 'passwd' or info == 'user') and len(val) >20:
                val - self.dec.fdec(val)
            dbinfo[info] = val
        return dbinfo
    
    def getNow(self):
        return self.com.getNow('%Y%m%d%H%M%S')
    
    
    def getHistMonth(self):
        return self.com.getNow('%Y%m%d')
    
    def queryExec(self,query):
        print(query)
        print(self.conn_string)
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
        print('query 2:', query)
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if rows == None:
            self.com.sysOut('Empty result set from query')
        
                
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
               
        
        except psycopg2.DatabaseError as e:
            if con:
                con.rollback()
            print('Error %s' % str(e))
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
            except psycopg2.DatabaseError as e:
                if con:
                    con.rollback()
                print('Error %s' % str(e))
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
        print(query)
        try:
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            cur.execute(query)
            con.commit()
        except psycopg2.DatabaseError as e:
            if con:
                con.rollback()
            print('Error %s' % str(e))
            sys.exit(1)
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

        except psycopg2.DatabaseError as e:
            if con:
                con.rollback()
            print('Error %s' % str(e))
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

        except psycopg2.DatabaseError as e:
            if con:
                con.rollback()
            print('Error %s' % str(e))
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
        except psycopg2.DatabaseError as e:
            if con:
                con.rollback()
            print('Error %s' % str(e))
            sys.exit(1)
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
            print("I am unable to connect to the database.")

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
    
    def getList(self,obj):
        conn = None
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
        except:
            print("I am unable to connect to the database.")
        query="SELECT * FROM vnstatus.vnstatus_%s_status;"%obj
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
    
    
    def esx_upsert(self,esxDicList):
        con = None
        
        con = psycopg2.connect(self.conn_string)
        cur = con.cursor()
        for esxDic in esxDicList:
            print(esxDic)
            status_date=esxDic['status_date']
            esx_ip = esxDic['esx_ip']
            helth_status=esxDic['ping_status']
            uuid = esxDic['uuid']
            print(esxDic)
            print (status_date,esx_ip,helth_status)
            query="""
            INSERT INTO vnstatus.vnstatus_esx_status (status_date,esx_ip,health_status,uuid,health_type,health_name) values ('%s','%s','%s','%s','PING_CHECK','PING_CHECK')
            """%(status_date,esx_ip,helth_status,uuid)
            print(query)
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
        except psycopg2.DatabaseError as e:
            if con:
                con.rollback()
            print('Error %s' % str(e))
            sys.exit(1)
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
                cur.execute(query)
            con.commit()
        except psycopg2.DatabaseError as e:
            if con:
                con.rollback()
            print('Error %s' % str(e))
            sys.exit(1)
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
    vmDic['vc_vcenter']='10.10.10.64'
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
    print(vmDicList)
    vmDicList.append(vmDic)
    print(FletaDb().upsert(vmDicList))
        