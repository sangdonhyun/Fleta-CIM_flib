#-*- coding: utf-8 -*-
import fletaDbms
import datetime

import sys

class event_out():
    def __init__(self):
        self.db=fletaDbms.FletaDb()
    
    
    def main(self):
        now=datetime.datetime.now()
        today = now.strftime('%Y-%m-%d')
        ys=now + datetime.timedelta(days=-1)
        ysday=ys.strftime('%Y-%m-%d')
        
        print today,ysday
        
        rangesec='300'
        
        
        query="""select  kk1.*,
   coalesce(device_alias, serial_number) device_serial
from (
   SELECT seq_no, log_date, check_date, event_date, serial_number, event_code, 
          event_level, q_event_level, desc_summary, desc_detail, device_type, 
          vendor_name, event_method, action_date, action_contents, user_id, 
          category_a, category_b, category_c, tmp
   FROM event.event_log
   where 
   log_date >= '<YESTERDAY>' and log_date <= '<TODAY>' and      
   (device_type = 'VCT' or device_type = 'HST') and         
   check_date::timestamp > now()::timestamp + interval '-300 minutes' and    
   serial_number not in (
      select target_dev_name serial_number from ref.ref_svr_event_prevent_setting_history 
      where start_time::date <= now() and end_time::date > now()
   ) and user_id = '' order by seq_no desc
)kk1 left join (
   select 
      v_center master_serial,
      v_center_alias device_alias
   from master.master_vcenter_info
   union all
   select 
      vim_hostsystem,
      vim_hostsystem_alias device_alias
   from master.master_host_info
)kk2 on kk1.serial_number = kk2.master_serial;
        """
#         print query
        query=query.replace('<YESTERDAY>',ysday)
        query=query.replace('<TODAY>',today)
#         qeury=query.replace('<RANGESEC>',rangesec)
#         print query
        query='select version()'
        rows=self.db.getRaw(query)
        
        for row in rows:
            print row


if __name__=='__main__':
    event_out().main()    