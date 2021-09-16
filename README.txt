파일 
	- Fleta-CIM_flib_20210824_source.zip (source 파일)
	- vcenter_info.zip (실행파일)
		vcenter_by_pyvmomi.py 
		vcenter_m_get.py 



FCIM base :
 vcenter_by_pyvmomi.py

vcenter 가 여러대 있을경우 ,
 venter_m_get.py ==> vcenter_by_pyvmomi.py 를 thread 로 실행

list.cfg 편집
[vcenter1]
ip=121.170.193.209  <= vcenter IP
username=administrator@vsphere.local  <= vcneter web console user
#username=VSPHERE.LOCAL/Administrator <= web console pass
password=Kes2719!
#port = 443   <= default
port = 50000


config.cfg
[server]
ip=121.170.193.201  <== fleta_recv.exe 가 수행중인 서버 
port = 54002         <== fleta_recv.exe PORT (파일 전송 port)

