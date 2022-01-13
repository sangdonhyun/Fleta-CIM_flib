import os
import redis
import configparser
import ast

class Redis():
    def __init__(self):
        
        self.cfg=self.getCfg()
        self.redis_ip=self.cfg.get('server','redis_ip')
        self.r = self.conn()

        
    def conn(self):
        return redis.Redis(host=self.redis_ip,port=6379,password='kes2719!')

    def getCfg(self):
        cfg=configparser.Rawconfigparser()
        cfgFile=os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def avg(self,avgInfoList):
        for avgInfo in avgInfoList:
            avtg_kye=avgInfo['avg_key']
            self.r.get()
    def setdic(self,dic):
        key=dic['last_key']
        val=dic['last_val']
        self.r.set(key,val)
    def run(self,resultlist):
        print('redis conn')
        """
        hset '2019-04-02 10:36:03::serial::flag' 'process(storage)' 'value'
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:54:00+00:00 cpu.usage.average 83 0.0
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:54:20+00:00 cpu.usage.average 77 0.0
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:54:40+00:00 cpu.usage.average 65 0.0
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:55:00+00:00 cpu.usage.average 88 0.0
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:55:20+00:00 cpu.usage.average 72 0.0
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:55:40+00:00 cpu.usage.average 70 0.0
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:56:00+00:00 cpu.usage.average 72 0.0
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:56:20+00:00 cpu.usage.average 75 0.0
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:56:40+00:00 cpu.usage.average 67 0.0
        564d2e7e-393a-b454-d7bd-a4688998dc92 2019-05-10 14:57:00+00:00 cpu.usage.average 83 0.0
        name=cpu.usage.average(%)
        key=564d2e7e-393a-b454-d7bd-a4688998dc92::2019-05-10 14:57:00+00:00
        value=0.0
        """
        for redisInfo in resultlist:

            """
            redisInfo['redis_key']='%s::%s'%(self.uuid,stats[0].sampleInfo[count].timestamp)
            redisInfo['redis_name']=perf_key
            redisInfo['redis_value']=float(val/100)
            """
            name,key,value='','',''
            
            """
            redisInfo['redis_key']=keys
            redisInfo['redis_filed']=avg3
            redisInfo['redis_value']=float(val/100)
            """
            
            key=redisInfo['redis_key']
            value=redisInfo['redis_value']
            
            
            if len(redisInfo) == 3:
                filed=redisInfo['redis_filed']
                self.r.hset(key,filed,value)
                print(key, filed, value)

            else:
                self.r.set(key,value)
            self.r.expire(key,"259200")

if __name__=='__main__':
#     with open('redis_in_temp.txt')  as f:
#         tmp=f.readlines()
    tmp="""{'redis_key': '564d64b6-b072-fff2-05bf-02280b1de1a5::2019-05-10 16:35:20+00:00', 'redis_value': 1.0, 'redis_filed': 'cpu.usage.average'}
{'redis_key': '564d64b6-b072-fff2-05bf-02280b1de1a5::2019-05-10 16:35:20+00:00', 'redis_value': 1.0, 'redis_filed': 'cpu.usage.average'}""".splitlines()
    """\
    hget "2019-05-15 20::4200454a-71cf-e743-a780-0032abccf0ad::W_2016_restapi_68::cpu::usage" "avg_count""
    """
    r=Redis().r
    ret=r.hget("2019-05-15 17::564d2e7e-393a-b454-d7bd-a4688998dc92::Linux_Redhat7.2_60::net::usag","avg_count")
print(ret, ret == None)
if ret==None:
        r.hset("2019-05-15 17::564d2e7e-393a-b454-d7bd-a4688998dc92::Linux_Redhat7.2_60::net::usag","avg_count","1")
    ret=r.hget("2019-05-15 17::564d2e7e-393a-b454-d7bd-a4688998dc92::Linux_Redhat7.2_60::net::usag","avg_count")
print(ret)

ret=r.hget("2019-05-15 17::564d2e7e-393a-b454-d7bd-a4688998dc92::Linux_Redhat7.2_60::net::usag","avg_count")
print(ret, ret == None)
if ret==None:
        r.hset("2019-05-15 17::564d2e7e-393a-b454-d7bd-a4688998dc92::Linux_Redhat7.2_60::net::usag","avg_count","1")
    ret=r.hget("2019-05-15 17::564d2e7e-393a-b454-d7bd-a4688998dc92::Linux_Redhat7.2_60::net::usag","avg_count")
print(ret)

ret=r.keys("2019-05-20 12::564d64b6-b072-fff2-05bf-02280b1de1a5*")
print(ret)
for k in ret:
        print(k)
        print(r.hget(k, 'avg'))
    
        