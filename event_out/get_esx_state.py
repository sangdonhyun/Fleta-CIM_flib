#-*- coding: utf-8 -*
#!/usr/bin/env python
"""
 Written by Lance Hasson
 Github: https://github.com/JLHasson

 Script to report all available realtime performance metrics from a
 virtual machine. Based on a Java example available in the VIM API 6.0
 documentationavailable online at:
 https://pubs.vmware.com/vsphere-60/index.jsp?topic=%2Fcom.vmware.wssdk.pg.
 doc%2FPG_Performance.18.4.html&path=7_1_0_1_15_2_4

 Requirements:
     VM tools must be installed on all virtual machines.
"""

from pyVmomi import vim
from pyVim.connect import SmartConnectNoSSL, Disconnect
import atexit
import sys
import datetime
import ConfigParser
import os, socket, struct, select, time
import fletaDbms
import fletaSnmp

class ping_check():
    def __init__(self):
        self.ICMP_ECHO_REQUEST = 8 # Seems to be the same on Solaris.
 
    def checksum(self,source_string):
        """
        I'm not too confident that this is right but testing seems
        to suggest that it gives the same answers as in_cksum in ping.c
        """
        sum = 0
        countTo = (len(source_string)/2)*2
        count = 0
        while count<countTo:
            thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
            sum = sum + thisVal
            sum = sum & 0xffffffff # Necessary?
            count = count + 2
     
        if countTo<len(source_string):
            sum = sum + ord(source_string[len(source_string) - 1])
            sum = sum & 0xffffffff # Necessary?
     
        sum = (sum >> 16)  +  (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
     
        # Swap bytes. Bugger me if I know why.
        answer = answer >> 8 | (answer << 8 & 0xff00)
     
        return answer
     
     
    def receive_one_ping(self,my_socket, ID, timeout):
        """
        receive the ping from the socket.
        """
        timeLeft = timeout
        while True:
            startedSelect = time.time()
            whatReady = select.select([my_socket], [], [], timeLeft)
            howLongInSelect = (time.time() - startedSelect)
            if whatReady[0] == []: # Timeout
                return
     
            timeReceived = time.time()
            recPacket, addr = my_socket.recvfrom(1024)
            icmpHeader = recPacket[20:28]
            type, code, checksum, packetID, sequence = struct.unpack(
                "bbHHh", icmpHeader
            )
            if packetID == ID:
                bytesInDouble = struct.calcsize("d")
                timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
                return timeReceived - timeSent
     
            timeLeft = timeLeft - howLongInSelect
            if timeLeft <= 0:
                return
     
     
    def send_one_ping(self,my_socket, dest_addr, ID):
        """
        Send one ping to the given >dest_addr<.
        """
        dest_addr  =  socket.gethostbyname(dest_addr)
     
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        my_checksum = 0
     
        # Make a dummy heder with a 0 checksum.
        header = struct.pack("bbHHh", self.ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
        bytesInDouble = struct.calcsize("d")
        data = (192 - bytesInDouble) * "Q"
        data = struct.pack("d", time.time()) + data
     
        # Calculate the checksum on the data and the dummy header.
        my_checksum = self.checksum(header + data)
     
        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        header = struct.pack(
            "bbHHh", self.ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
        )
        packet = header + data
        my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1
     
     
    def do_one(self,dest_addr, timeout):
        """
        Returns either the delay (in seconds) or none on timeout.
        """
        icmp = socket.getprotobyname("icmp")
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error, (errno, msg):
            if errno == 1:
                # Operation not permitted
                msg = msg + (
                    " - Note that ICMP messages can only be sent from processes"
                    " running as root."
                )
                raise socket.error(msg)
            raise # raise the original error
     
        my_ID = os.getpid() & 0xFFFF
     
        self.send_one_ping(my_socket, dest_addr, my_ID)
        delay = self.receive_one_ping(my_socket, my_ID, timeout)
     
        my_socket.close()
        return delay
     
     
    def verbose_ping(self,dest_addr, timeout = 10, count = 5):
        """
        Send >count< ping to >dest_addr< with the given >timeout< and display
        the result.
        """
        for i in xrange(count):
    #        print "ping %s..." % dest_addr,
            try:
                delay  =  self.do_one(dest_addr, timeout)
            except socket.gaierror, e:
    #            print "falsed. (socket error: '%s')" % e[1]
                return False
                break
     
            if delay  ==  None:
    #            print "falsed. (timeout within %ssec.)" % timeout
                return False
            else:
                delay  =  delay * 1000
    #            print "get ping in %0.4fms" % delay
                return True
    

class vm_Perform():
    def __init__(self):
        self.ping=ping_check()
        self.db=fletaDbms.FletaDb()
        
        self.oldEsxStatus = self.oldEsxStatus()
        self.esxDicList=[]
        self.snmp=fletaSnmp.Load()
    
    def getVcList(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','list.cfg')
        cfg.read(cfgFile)
        vcList=[]
        for sec in cfg.sections():
            vc={}
            vc['name']=sec
            for opt in cfg.options(sec):
                vc[opt]=cfg.get(sec,opt)
            vcList.append(vc)
        return vcList    
    def oldEsxStatus(self):
        oldEsxStatus={}
        oldEsxList=self.db.getList('esx')

        for oldesx in oldEsxList:
            print oldesx
            oldEsxStatus[oldesx[1]]=oldesx[2]
        return oldEsxStatus

    def GetVMHosts(self,content):
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj
    
    def host_perform(self,vcInfo):
        vc_host=vcInfo['ip']
        vc_user=vcInfo['username']
        vc_pwd=vcInfo['password']
        vc_port = vcInfo['port']
        try:
            si = SmartConnectNoSSL(
                host=vc_host,
                user=vc_user,
                pwd=vc_pwd,
                port=int(vc_port))
            atexit.register(Disconnect, si)
        except IOError as e:
            pass
    
        if not si:
            raise SystemExit("Unable to connect to host with supplied info.")
        
        content = si.RetrieveContent()
        
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        hosts=[host for host in host_view.view]
        host_view.Destroy()
        print hosts
        
        """
        Obtains the current CPU usage of the Host
    
        :param host_moref: Managed Object Reference for the ESXi Host
        """
        status_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        
        for host in hosts:
            esxDic={}
            
#             print host.summary
            print 'hostname',host.name
            uuid=host.hardware.systemInfo.uuid.strip()
            ip=host.name.strip()
            ping_status=self.ping.verbose_ping(ip)
            print ping_status
            esxDic['esx_uuid'] = uuid
            esxDic['status_date'] = status_date
            esxDic['esx_ip']=ip
            esxDic['ping_status']=str(ping_status)
            esxDic['vc_vcenter']=vc_host
            self.esxDicList.append(esxDic)
    
    
    
    def snmp_send(self,smsInfo):
        
        errDic={}
        errDic['serial']=smsInfo['esx_uuid']
        errDic['event_date']=smsInfo['status_date']
        errDic['event_code']='vm-guest001'
        errDic['severity']='Warning'
        errDic['desc']=smsInfo['desc']
        errDic['vendor']='VMware'
        errDic['device_type']='ESX'
        errDic['method'] = 'snmp'
        errDic['etc'] =str(smsInfo)
        print (errDic)
        try:
            self.snmp.errSnmpTrapSendV3(errDic)
        except:
            pass
    
        
    def main(self):
#         self.vmGuest()
        smsList=[]
        vcList=self.getVcList()
        for vc in vcList:
            self.host_perform(vc)

        
        print self.esxDicList   
        if self.oldEsxStatus == {}:
            self.db.esx_upsert(self.esxDicList)
            return 
        smsList=[]
        for esx in self.esxDicList:
            esx_ip=esx['esx_ip']
            if esx_ip not in self.oldEsxStatus.keys():
                msg='new esx host ip:'
                esx['desc'] = msg
                smsList.append(esx)
                print msg
            else:
                if esx_ip=='':
                    pass
                
                print esx_ip,esx['ping_status']
                print esx['ping_status']==self.oldEsxStatus[esx_ip]
                print esx['ping_status'],self.oldEsxStatus[esx_ip]
                print str(esx['ping_status']) == 'True'
                if str(esx['ping_status']) == 'True': 
                    msg='[MXG SMS] vmweare Server Alert: esx host ping check fail (esx : %s , vcenter : %s)'%(esx_ip,esx['vc_vcenter'])
                    esx['desc'] = msg
                    print msg
                    print esx
                    smsList.append(msg)
                    self.snmp_send(esx)
        print 'sms List :'
        print smsList
        return smsList
        
        self.db.esx_upsert(self.esxDicList)            
if __name__ == "__main__":
    vm_Perform().main()
