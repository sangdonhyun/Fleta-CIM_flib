#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
	Created on 2019.07.01
	@author: chyi
'''
import time
import os
import sys
import ConfigParser

sCurPath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])))
LOG_PATH = sCurPath + "/logs/"

class Log_(object):
	def __init__(self):
		if os.path.isdir(LOG_PATH) == False:
			os.mkdir(LOG_PATH)
		self.o_log_code = ConfigParser.ConfigParser()


	def logdata(self, s_file_name, s_file_type, s_code ='', s_refer_val=''):
		if os.path.isdir(LOG_PATH) == False:
			os.mkdir(LOG_PATH)
		s_refer_val = str(s_refer_val)
		s_data = "[%s] " % (s_code)
		if s_refer_val != '':
			s_data = s_data + " ==> " + s_refer_val

		today = time.strftime("%Y%m%d", time.localtime(time.time()))
		# filefullname = LOG_PATH + s_file_name + "_" + str(today) + "_" + s_file_type + ".log"
		filefullname = LOG_PATH + str(today) + "_" + s_file_name + "_" + s_file_type + ".log"

		fp = file(filefullname, 'a+')
		now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
		comment = "[" + str(now) + "] " + str(s_data) + "\n"
		fp.write(comment)
		fp.close()
