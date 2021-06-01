# -*- coding: UTF8 -*-
'''
Created on 2019. 8. 30.

@author: user
'''
import cx_Oracle
import os
import datetime
import fletaDbms
os.environ['NLS_LANGUAGE']='AMERICAN'
"""
sqlplus fletauser/fletapass
"""
# PORT_NUM = 1521
# dsn = cx_Oracle.makedsn("121.170.193.220", PORT_NUM, "orcl")
# db = cx_Oracle.connect("fletauser", "fletapass", dsn)
# cursor = db.cursor()
# 
# cursor.execute("""select * from eventout;""")
# row = cursor.fetchone()
# while row:
#     print(str(row[0]) )
#     row = cursor.fetchone()


class Event():
    def __init__(self,event_list):
        self.tday=datetime.datetime.now().strftime('%Y%m%d')
        self.eventList=fletaDbms.FletaDb().getEvent()
        self.event_list=event_list
        
    def getID(self):
        PORT_NUM = 1510
        dsn = cx_Oracle.makedsn("10.134.247.17", PORT_NUM, "psdlsdb1")
        db = cx_Oracle.connect("dbmonsms", "dbmonsms!!00", dsn)
        cursor = db.cursor()
        query="""
        SELECT TO_CHAR(SYSDATE, 'YYYYMMDD') || LPAD(SEQ_MSG_SEND_ID.NEXTVAL,7,'0') AS V_MSG_SEND_ID FROM DUAL
        """
        cursor.execute(query)
        row = cursor.fetchone()
        V_MSG_SEND_ID=row[0]
        print 'V_MSG_SEND_ID :',V_MSG_SEND_ID
        query="""
        SELECT LEMPUSR.FN_GET_PUSH_CMID_SEQ() AS V_REF_SEND_MSG_ID FROM DUAL
        """
        cursor.execute(query)
        row = cursor.fetchone()
        V_REF_SEND_MSG_ID=row[0]
        print 'V_REF_SEND_MSG_ID :',V_REF_SEND_MSG_ID	
        cursor.close()
        db.close()
        return V_MSG_SEND_ID,V_REF_SEND_MSG_ID

    
    def setEvent(self,tel_no,event_msg):
        PORT_NUM = 1510
        dsn = cx_Oracle.makedsn("10.134.247.17", PORT_NUM, "psdlsdb1")
        db = cx_Oracle.connect("dbmonsms", "dbmonsms!!00", dsn)
        cursor = db.cursor()


        query="""
        SELECT TO_CHAR(SYSDATE, 'YYYYMMDD') || LPAD(SEQ_MSG_SEND_ID.NEXTVAL,7,'0') AS V_MSG_SEND_ID FROM DUAL
        """
        cursor.execute(query)
        row = cursor.fetchone()
        V_MSG_SEND_ID=row[0]
        print 'V_MSG_SEND_ID :',V_MSG_SEND_ID
        query="""
        SELECT LEMPUSR.FN_GET_PUSH_CMID_SEQ() AS V_REF_SEND_MSG_ID FROM DUAL
        """
        cursor.execute(query)
        row = cursor.fetchone()
        V_REF_SEND_MSG_ID=row[0]
        print 'V_REF_SEND_MSG_ID :',V_REF_SEND_MSG_ID
        

        
        insquery="""
        INSERT INTO TCM_MSG_SEND
    (
        MSG_SEND_ID
        ,CRE_USR_ID
        ,CRE_DTM
        ,CRE_PGM_ID
        ,UPT_USR_ID
        ,UPT_DTM
        ,UPT_PGM_ID
        ,MSG_RCPR_CPNO
        ,MSG_SNDR_TEL
        ,MSG_SEND_MDIA_CD
        ,SEND_TME_CYCL_CD
        ,SEND_PRGS_STAT_CD
        ,USFE_REQ_ORGT_SCT_CD
        ,USFE_REQ_ORGT_CD
        ,MSG_SEND_ORGT_SCT_CD
        ,MSG_SEND_ORGT_CD
        ,MSG_SEND_USR_ID
        ,ATMT_CRE_MSG_YN
    )
    VALUES
    (
        '%s'
        ,'SYSTEM'
        ,SYSDATE
        ,'SYSTEM'
        ,'SYSTEM'
        ,SYSDATE
        ,'SYSTEM'
        ,%s
        ,'15882121'
        ,'3'
        ,'1'
        ,'2'
        ,'00'
        ,'00000'
        ,'00'
        ,'00000'
        ,'SYSTEM'
        ,'N'
    )
    
        """%(V_MSG_SEND_ID,tel_no)
        print insquery
        print '-'*30
        cursor.execute(insquery)
        db.commit()
        insquery="""
        
    INSERT INTO TCM_MDIA_CLB_MSG
    (
        MSG_SEND_ID
        ,MSG_SEND_MDIA_CD
        ,CRE_USR_ID
        ,CRE_DTM
        ,CRE_PGM_ID
        ,UPT_USR_ID
        ,UPT_DTM
        ,UPT_PGM_ID
        ,SEND_PRGS_STAT_CD
        ,MSG_CONT
        ,MSG_SEND_ACTG_CORP_ID
    )
    VALUES
    (
        '%s'
        ,'3'
        ,'SYSTEM'
        ,SYSDATE
        ,'SYSTEM'
        ,'SYSTEM'
        ,SYSDATE
        ,'SYSTEM'
        ,'2'
        ,'%s'
        ,'210'   
    )

        """%(V_MSG_SEND_ID,event_msg)

        print insquery
        print '-'*30
        
        cursor.execute(insquery)
        db.commit()
        insquery="""
        
    INSERT INTO TCM_MDIA_CLB_MSG_RST
    (
        MSG_SEND_ID
        ,MSG_SEND_MDIA_CD
        ,REF_SEND_MSG_ID
        ,CRE_USR_ID
        ,CRE_DTM
        ,CRE_PGM_ID
        ,UPT_USR_ID
        ,UPT_DTM
        ,UPT_PGM_ID
        ,SEND_PRGS_STAT_CD
    )
    VALUES
    (
        '%s'
        ,'3'
        ,%s
        ,'SYSTEM'
        ,SYSDATE
        ,'SYSTEM'
        ,'SYSTEM'
        ,SYSDATE
        ,'SYSTEM'
        ,'2'
    )
        """%(V_MSG_SEND_ID,V_REF_SEND_MSG_ID)
        print insquery
        print '-'*30
        
        cursor.execute(insquery)
        db.commit()
        
        
        query="""                   INSERT INTO KMP_MSG
        (
                CMID
                ,MSG_TYPE
                ,STATUS
                ,REQUEST_TIME
                ,SEND_TIME
                ,DEST_PHONE
                ,SEND_PHONE
                ,MSG_BODY
                ,NATION_CODE
                ,SENDER_KEY
                ,TEMPLATE_CODE
        )
        VALUES (
                '%s'
                ,'6'
                ,'0'
                ,SYSDATE
                ,SYSDATE
                ,'%s'
                ,'15882121'
                ,'%s'
                ,'82'
                ,'1dc95c8fd8cc510e5f8842582fb3ab5b985089f2'
                ,'LMSG_20190418210431714771'
        )
        """%(V_REF_SEND_MSG_ID,tel_no,event_msg)
        print query
        cursor.execute(query)
        db.commit()

        
        print query
        print '-'*30
        
        
        cursor.close()
        db.close()
        return V_MSG_SEND_ID,V_REF_SEND_MSG_ID

    def selectQeury(self,V_MSG_SEND_ID,V_REF_SEND_MSG_ID):
        PORT_NUM = 1510
        dsn = cx_Oracle.makedsn("10.134.247.17", PORT_NUM, "psdlsdb1")
        db = cx_Oracle.connect("dbmonsms", "dbmonsms!!00", dsn)
        cursor = db.cursor()

        query="""
        SELECT * FROM TCM_MSG_SEND WHERE MSG_SEND_ID='%s'
        """%V_MSG_SEND_ID
        print query
        cursor.execute(query)
        row = cursor.fetchone()

        print row
        print '-'*50
        query="""
        SELECT * FROM TCM_MDIA_CLB_MSG WHERE MSG_SEND_ID='%s'
        """%V_MSG_SEND_ID
        print query
        cursor.execute(query)
        row = cursor.fetchone()

        print row
        print '-'*50
        query="""
        SELECT * FROM TCM_MDIA_CLB_MSG_RST WHERE MSG_SEND_ID='%s'
        """%V_MSG_SEND_ID


        print query
        cursor.execute(query)
        row = cursor.fetchone()

        print row
        print '-'*50
        query="""
        SELECT * FROM KMP_MSG WHERE CMID='%s'
        """%V_REF_SEND_MSG_ID

        print query
        cursor.execute(query)
        row = cursor.fetchone()
        print row
        print '-'*50

        cursor.close()
        db.close()


    def test(self):
        tel_no='01042420660'
    
    
    def set_message(self,vm_name,vc_name,dev,val,threshold):
        event_msg="[MXG SMS] {} ({}) vmware guest Server {} Alert: {} (defalt : {})".format(vm_name,vc_name,dev,val,threshold)
        return event_msg
    
    def main(self):
        #tel_no='01026872964'
        #tel_no='01090915401'
        tel_no='01042420660'
        
        for event in self.event_list:
            
            print event
            "[MXG SMS] {p$sid$} Server Alert: p$resource_name$ (p$string_level$:p$value$) p$description$"
            event_msg="[MXG SMS] vmware Server Alert: %s"%event.strip()
            print event_msg
            
            V_MSG_SEND_ID,V_REF_SEND_MSG_ID=self.setEvent(tel_no,event_msg)
            self.selectQeury(V_MSG_SEND_ID,V_REF_SEND_MSG_ID)
             
if __name__=='__main__':
    Event().main()
        
