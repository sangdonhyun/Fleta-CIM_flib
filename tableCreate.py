'''
Created on 2019. 5. 15.

@author: Administrator
'''



import datetime
import psycopg2

t0 = datetime.datetime(2019, 5, 1)


class DB():
    def __init__(self):
        self.conn_string = "host='121.170.193.196' dbname='fleta' user='webuser' password='qw19850802@'"
    def getRow(self,query):
        try:
            db=psycopg2.connect(self.conn_string)
            cursor = db.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            db.close()
            return rows
        except:
            return None

    def insDb(self,query):
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
        finally:
            if con:
                con.close()
                
                
    
class TableCreaet():
    def __init__(self):
        self.db=DB()
        self.now=datetime.datetime.now()
        self.tableName=self.getTableName(self.now)
        self.dateStr=self.now.strftime('%Y-%m-%d')
    
    def getTableName(self,targetDatet):
        timestr=targetDatet.strftime('y%Ym%md%d')
        tname='monitor.perform_stg_avg_{}'.format(timestr)
        return tname
    
    
    def isTable(self,tablename):
        
        schema,tb= tablename.split('.')
        query="select count(*) from  pg_tables where tablename='{}' and schemaname='{}'".format(tb,schema)
        ret=self.db.getRow(query)
        if ret==None :
            return False
        else:
            if ret[0][0]!=0:
                print '{} table exist '.format(tablename)
                return True
            else:
                return False
        
        
        
        
    def createTable(self):
        query=""
        for i in range(3):
            
            td=self.now+datetime.timedelta(days=i)
            
            dateStr=td.strftime('%Y-%m-%d')
            tbStr=td.strftime('y%Ym%md%d')
            tb='monitor.perform_stg_avg_{}'.format(tbStr)
            print tb
            
            if not self.isTable(tb):
                query += """
CREATE TABLE {} (
CHECK ( ins_date = DATE '{}')
) INHERITS (monitor.perform_stg_avg);
            """.format(tb,self.dateStr)
            
        
        return query

    def getTbList(self):
        today= self.now.strftime('%Y-%m-%d')
        
        dayList=[]
        tbList=[]
        for i in range(7):
            td= self.now+datetime.timedelta(days=i)
            dayList.append(td.strftime('%Y-%m-%d'))
            tbStr=td.strftime('y%Ym%md%d')
            print tbStr
            tb='monitor.perform_stg_avg_{}'.format(tbStr)
            tbList.append(tb)
        
        for i in range(7):
            td= self.now+datetime.timedelta(days=-i)
            
            tbStr=td.strftime('y%Ym%md%d')
            tb='monitor.perform_stg_avg_{}'.format(tbStr)
            
            if tb not in tbList:
                print tbStr
                dayList.append(td.strftime('%Y-%m-%d'))
                tbList.append(tb)

        return sorted(set(dayList)),sorted(set(tbList))
    def trigger(self):
        daylist,tbList = self.getTbList()
        
        query="""
CREATE OR REPLACE FUNCTION monitor.perform_stg_avg_insert_trigger()
  RETURNS trigger AS
$BODY$
BEGIN
    """
        for i in range(len(daylist)):
            
            if i == 0:
                ifstr='IF '
            else:
                ifstr='\nELSIF'
        
            query=query+"""{}  NEW.ins_date = DATE '{}' THEN
            INSERT INTO {} VALUES (NEW.*);""".format(ifstr,daylist[i],tbList[i])
        query=query+"""
    ELSE
    RAISE EXCEPTION 'Date out of range.  Fix the monitor.perform_stg_avg_insert_trigger() function!';
    END IF;
    RETURN NULL;
    
    
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION monitor.perform_stg_avg_insert_trigger()
  OWNER TO webuser;
        """
        
        return query
    
    def main(self):
        tname=self.getTableName(self.now)
        query=self.createTable()
        print query
        # table create
        self.db.insDb(query)
        # trigger create or replace
        trigger_query=self.trigger()
        print trigger_query
        self.db.insDb(trigger_query)
    
if __name__=='__main__':
    
    TableCreaet().main()
    