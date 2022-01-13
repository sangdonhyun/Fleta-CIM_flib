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
#import common
import datetime
import performlog
import inspect
from inspect import currentframe, getframeinfo


class FletaDb():
	def __init__(self):
		#self.com = common.Common()
		#self.dec = common.Decode()
#		  self.logger = self.com.flog()
				
#		  self.conn_string = "host='localhost' dbname='fleta' user='fletaAdmin' password='kes2719!'"
		self.conn_string = self.getConnStr()
#		  print self.conn_string
		self.cfg = self.getCfg()
		self.cLogCheck = performlog.Log_()
		
	
	def getCfg(self):
		cfg = configparser.RawConfigParser()
		cfgFile = os.path.join('config','RDBload.cfg')
		cfg.read(cfgFile)
		return cfg
	
	def getConnStr(self):
		cfg = configparser.RawConfigParser()
		cfgFile = os.path.join('config','RDBload.cfg')
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
			dbname = 'qweb'
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
		tNowTime = datetime.datetime.now()
		return tNowTime.strftime('%Y%m%d%H%M%S')
		
	def getHistMonth(self):
		tNowTime = datetime.datetime.now()
		return tNowTime.strftime('%Y%m%d')
		
	def queryExec(self,query):
		print query
		print self.conn_string
		con = None
#		  try:
		con = psycopg2.connect(self.conn_string)
		cur = con.cursor()
		
		cur.execute(query)
		con.commit()
#			  print "Number of rows updated: %d" % cur.rowcount
#		  except psycopg2.DatabaseError, e:
#			  if con:
#				  con.rollback()
#			  print 'Error %s' % e	  
#			  sys.exit(1)
#		  finally:
#			  if con:
#				  con.close()
	
	def isEvnt(self,query):
	
		db=psycopg2.connect(self.conn_string)
		cursor = db.cursor()
		print 'query 2:',query
		cursor.execute(query)
		rows = cursor.fetchall()
		
		#if rows == None:
		#	 self.com.sysOut('Empty result set from query')
		
				
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
			
#			  print "Number of rows updated: %d" % cur.rowcount
			   
		
		except psycopg2.DatabaseError, e:
			
			if con:
				con.rollback()
			cFrameinfo = getframeinfo(currentframe())
			""" Line on occurred exception : cTraceBack.tb_lineno """
			cTraceBack = sys.exc_info()[-1]
			sLineNo = str(cTraceBack.tb_lineno)
			sExcept = ''
			if inspect.stack()[1][3]:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e) + 'caller : ' + inspect.stack()[1][3] + ' line - %s' %inspect.stack()[1][2]
			else:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e)
			self.cLogcheck.logdata('DBMS', 'ERROR', cFrameinfo.filename, sExcept)
			
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
#		  print query
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
				cFrameinfo = getframeinfo(currentframe())
				""" Line on occurred exception : cTraceBack.tb_lineno """
				cTraceBack = sys.exc_info()[-1]
				sLineNo = str(cTraceBack.tb_lineno)
				sExcept = ''
				if inspect.stack()[1][3]:
					sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e) + 'caller : ' + inspect.stack()[1][3] + ' line - %s' %inspect.stack()[1][2]
				else:
					sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e)
				self.cLogcheck.logdata('DBMS', 'ERROR', cFrameinfo.filename, sExcept)
				
				print 'Error %s' % e
				sys.exit(1)
			finally:
				if con:
					con.close()
			qList.append(query)
		return qList
	def dicInsert(self,dic,table='monitor.perform_stg_avg'):
		
		print 'TABLE:',table
		print dic
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
			cFrameinfo = getframeinfo(currentframe())
			""" Line on occurred exception : cTraceBack.tb_lineno """
			cTraceBack = sys.exc_info()[-1]
			sLineNo = str(cTraceBack.tb_lineno)
			sExcept = ''
			if inspect.stack()[1][3]:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e) + 'caller : ' + inspect.stack()[1][3] + ' line - %s' %inspect.stack()[1][2]
			else:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e)
			self.cLogcheck.logdata('DBMS', 'ERROR', cFrameinfo.filename, sExcept)
			
			print 'Error %s' % e	
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
#		  print query
	
	def dbInsertDicList(self,dicList,table='monotir.pm_auto_isilon_info'):
		qList=self.getQList(dicList, table)
		con = None
		
		try:
			
			con = psycopg2.connect(self.conn_string)
			cur = con.cursor()
			for q in qList:
				
				cur.execute(q)
			con.commit()
			 
#			  print "Number of rows updated: %d" % cur.rowcount
				
		 
		except psycopg2.DatabaseError, e:
			 
			if con:
				con.rollback()
			cFrameinfo = getframeinfo(currentframe())
			""" Line on occurred exception : cTraceBack.tb_lineno """
			cTraceBack = sys.exc_info()[-1]
			sLineNo = str(cTraceBack.tb_lineno)
			sExcept = ''
			if inspect.stack()[1][3]:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e) + 'caller : ' + inspect.stack()[1][3] + ' line - %s' %inspect.stack()[1][2]
			else:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e)
			self.cLogcheck.logdata('DBMS', 'ERROR', cFrameinfo.filename, sExcept)
			 
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
#		  print query
		self.qwrite(query)
		con = None
		 
		try:
			  
			con = psycopg2.connect(self.conn_string)
			cur = con.cursor()
#						  
			cur.execute(query)
			con.commit()
			 
#			  print "Number of rows updated: %d" % cur.rowcount
		 
		except psycopg2.DatabaseError, e:
			 
			if con:
				con.rollback()
			cFrameinfo = getframeinfo(currentframe())
			""" Line on occurred exception : cTraceBack.tb_lineno """
			cTraceBack = sys.exc_info()[-1]
			sLineNo = str(cTraceBack.tb_lineno)
			sExcept = ''
			if inspect.stack()[1][3]:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e) + 'caller : ' + inspect.stack()[1][3] + ' line - %s' %inspect.stack()[1][2]
			else:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e)
			self.cLogcheck.logdata('DBMS', 'ERROR', cFrameinfo.filename, sExcept)
			 
			print 'Error %s' % e	
			sys.exit(1)
			 
		finally:
			 
			if con:
				con.close()
		
	def dbQueryIns(self,query):
		con = None
		#print query
		con = psycopg2.connect(self.conn_string)
		cur = con.cursor()
		cur.execute(query)
		con.commit()
		con.close()
		
		
		
	def eventList(self):
		db=psycopg2.connect(self.conn_string)
		cursor = db.cursor()
		
		query_string = self.getQuery()
		cursor.execute(query_string)
		rows = cursor.fetchall()
		
		#if rows == None:
		#	 self.com.sysOut('Empty result set from query')
		
				
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
			cFrameinfo = getframeinfo(currentframe())
			""" Line on occurred exception : cTraceBack.tb_lineno """
			cTraceBack = sys.exc_info()[-1]
			sLineNo = str(cTraceBack.tb_lineno)
			sExcept = ''
			if inspect.stack()[1][3]:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e) + 'caller : ' + inspect.stack()[1][3] + ' line - %s' %inspect.stack()[1][2]
			else:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e)
			
			self.cLogcheck.logdata('DBMS', 'ERROR', cFrameinfo.filename, sExcept)

			return []
	
	
	
	def isEvtByQeury(self,query):
	   
	   
		conn = None
		try:
			 
			conn = psycopg2.connect(self.conn_string)
			cur = conn.cursor()
			
			
		except:
			cFrameinfo = getframeinfo(currentframe())
			""" Line on occurred exception : cTraceBack.tb_lineno """
			cTraceBack = sys.exc_info()[-1]
			sLineNo = str(cTraceBack.tb_lineno)
			sExcept = ''
			if inspect.stack()[1][3]:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e) + 'caller : ' + inspect.stack()[1][3] + ' line - %s' %inspect.stack()[1][2]
			else:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e)
			self.cLogcheck.logdata('DBMS', 'ERROR', cFrameinfo.filename, sExcept)
			print "I am unable to connect to the database."
		
		# If we are accessing the rows via column name instead of position we 
		# need to add the arguments to conn.cursor.
		
#		  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

		try:
			cur.execute(query)
		except:
			cFrameinfo = getframeinfo(currentframe())
			""" Line on occurred exception : cTraceBack.tb_lineno """
			cTraceBack = sys.exc_info()[-1]
			sLineNo = str(cTraceBack.tb_lineno)
			sExcept = ''
			if inspect.stack()[1][3]:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e) + 'caller : ' + inspect.stack()[1][3] + ' line - %s' %inspect.stack()[1][2]
			else:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e)
			self.cLogcheck.logdata('DBMS', 'ERROR', cFrameinfo.filename, sExcept)
		
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
			cFrameinfo = getframeinfo(currentframe())
			""" Line on occurred exception : cTraceBack.tb_lineno """
			cTraceBack = sys.exc_info()[-1]
			sLineNo = str(cTraceBack.tb_lineno)
			sExcept = ''
			if inspect.stack()[1][3]:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e) + 'caller : ' + inspect.stack()[1][3] + ' line - %s' %inspect.stack()[1][2]
			else:
				sExcept = inspect.stack()[0][3] + ' ' + sLineNo + ' : ' + str(e)
			self.cLogcheck.logdata('DBMS', 'ERROR', cFrameinfo.filename, sExcept)
		
			pass

if __name__ == '__main__':
	"""
	2019-05-15 13:15:40::4200454a-71cf-e743-a780-0032abccf0ad::W_2016_restapi_68::cpu::usage average 29.0
	"""
	query='''
	INSERT INTO monitor.perform_stg_avg(
			ins_date,check_date, ctrl_unum, 
			flag_nm, cols_nm, cols_value_max, cols_max_date, cols_value_avg)
	VALUES ('2019-05-15', '2019-05-15 14', '4200454a-71cf-e743-a780-0032abccf0ad', 
		'cpu_usage', 'average', '57', '2019-05-15 13:14:23', '29');
	'''
	print query
	dbDicList=[]
	dbDic={}
	dbDic['ins_date']='2019-05-15'
	dbDic['check_date']='2019-05-15 15'
	dbDic['ctrl_unum']='4200454a-71cf-e743-a780-0032abccf0ad'
	dbDic['flag_nm']='cpu_usage'
	dbDic['cols_nm']='average'
	dbDic['cols_value_max']='57'
	dbDic['cols_max_date']='2019-05-15 13:14:23'
	dbDic['cols_value_avg']='29'
	dbDicList.append(dbDic)
	
#	  print FletaDb().queryExec(query)
	print FletaDb().dicInsert(dbDicList)
	
	
		