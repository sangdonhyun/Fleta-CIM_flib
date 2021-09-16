'''
Created on 2014. 4. 16.

@author: Administrator
'''
import threading, time
import socket
import os
import sys
import ast
import glob
import random
import datetime
import base64
import hashlib
import re

fcim_server = '121.170.193.207'
fcim_port = 54002
sock_retry_cnt = 5


class Decode():

    def _en(self, _in):
        return base64.b64encode(_in)

    def _de(self, _in):
        return base64.b64decode(_in)

    def fenc(self, str):
        e0 = self._en(str)
        e1 = self._en(e0)
        m = hashlib.md5(e0).hexdigest()
        e1 = e1.replace('=', '@')
        e = e1 + '@' + m
        return e

    def fdec(self, e):
        r = e.rfind('@')
        if r == -1:
            pass
        d1 = e[:r]
        d1 = d1.replace('@', '=')
        d0 = self._de(d1);
        d = self._de(d0);
        return d

    def decBit(self, fileName):
        with open(fileName) as f:
            tmp = f.read()
        if re.search('###\*\*\*', tmp):
            return True
        else:
            return False

    def fileDec(self, fileName):
        if self.decBit(fileName):
            return None
        with open(fileName) as f:
            str = f.read()
        with open(fileName, 'w') as f:
            f.write(self.fdec(str))
        return self.decBit(fileName)

    def fileDecReText(self, fileName):
        if self.decBit(fileName):
            with open(fileName) as f:
                reList = f.read()

        else:
            with open(fileName) as f:
                str = f.read()
            reList = self.fdec(str)

        return reList

    def fileEncDec(self, fileName):
        if self.decBit(fileName) == False:
            return None
        with open(fileName) as f:
            str = f.read()
        with open(fileName, 'w') as f:
            f.write(self.fenc(str))
        return self.decBit(fileName)


class SocketSender():
    def __init__(self,**kwargs):
        self.filieName=kwargs['FILENAME']
        self.dir = kwargs['DIR']
        self.HOST=fcim_server
        self.PORT=fcim_port

    def send(self):
#         HOST, PORT = "1.217.179.141", 54001
        HOST = self.HOST
        try:
            PORT = int(self.PORT)
        except:
            PORT=54001
        
        fname = self.filieName

        info={}
        info['FLETA_PASS']='kes2719!'
        info['FILENAME']=os.path.basename(fname)
        info['DIR']=self.dir
        info['FILESIZE']=os.path.getsize(fname)

        dec=Decode()

        data=dec.fenc(str(info))
        # print data

        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sBit=False
        
        try:
            # Connect to server and send data
            sock.connect((HOST, PORT))
            sock.sendall(data + "\n")
        
            # Receive data from the server and shut down
            received = sock.recv(1024)
            print (received)
            if received=='READY':
                with open(fname) as f:
                    data=f.read()
                sock.sendall(data)
            sBit = True
        except socket.error as e:
            sBit = False
            print (str(e))
        finally:
            sock.close()
        
        return sBit
    
    def main(self):
        reCnt=sock_retry_cnt
        cnt=0
        while 1:
            sBit=self.send()
            if sBit :
                print ("FILE TRANSFER SUCC BY SOCKET")
                break
            else:
                print ('FLETA SERVER : %s , PORT : %s SEND FILE ERROR RETRY (%d/%d) '%(self.HOST,self.PORT,cnt+1,reCnt))
            cnt += 1
            if reCnt == cnt:
                break 
            
            time.sleep(random.randint(5,10))
    
if __name__=='__main__':

    hostname = os.popen('hostname').read().strip()


    date_str=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    p_file = os.path.join('{}_{}.txt'.format(hostname,date_str))
    cmd = 'esxtop -b -a -d 10 -n 3 > {}'.format(p_file)
    ret=os.popen(cmd).read()
    if os.path.isfile(p_file):
        SocketSender(FILENAME=p_file,DIR='fcim\esx_perfrom.SCH').main()
