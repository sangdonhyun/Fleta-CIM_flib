'''
Created on 2019. 6. 12.

@author: Administrator
'''
"""
event manager
alarm manager


start time : ./config/%s_dTime.txt %vcenter
end time   : now

delay time : 60
"""

import vcenter_event_daily
import vcenter_host_alarms
import time

while True:
    vcenter_event_daily.Manager().main()
    vcenter_host_alarms.Manager().main()
    time.sleep(60)