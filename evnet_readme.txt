vcenter_event.py
	* v-center API (RestAPI) 에서 alarm manager 의 alarm event 전송

	content = si.RetrieveContent()
	am = content.alarmManager
	alarms = am.GetAlarm(content.rootFolder) # get all alarms



vcenter_host_alarm.py
	* v-center API (RestAPI) 중 Host 정보의 Alarm status 값에 대한 Event

	host_uuid=host.summary.hardware.uuid
	INDEX = si.content.searchIndex
	HOST = INDEX.FindByUuid(datacenter=None, uuid=host_uuid, vmSearch=False)
	alarms = HOST.triggeredAlarmState



vcenter_event_daily.py
	* v-center API (RestAPI) 중 Event manager 의 Event 값에 대한 Event

	filter_spec = vim.event.EventFilterSpec(eventTypeId=event_type_list, time=time_filter)
	eventManager = self.si.content.eventManager
	event_collector = eventManager.CreateCollectorForEvents(filter_spec)

	events_in_page = event_collector.ReadNextEvents(page_size)
	num_event_in_page = len(events_in_page)
	if num_event_in_page == 0:
		break
	events.extend(events_in_page)
	eventType not in  ['UserLoginSessionEvent','UserLogoutSessionEvent']:

vcenter_vm_health.py
    * vm
    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
    obj = [host for host in host_view.view]
    health = host.runtime.healthSystemRuntime.systemHealthInfo.numericSensorInfo
    if not i.healthState.label == 'Green':
        event 발생


event_out/get_esx_status.py
    * vm host 의 ping check 값에 --> vnsate.vnstat_esx_status 에 update
	content = si.RetrieveContent()
	host_view = content.viewManager.CreateContainerView(content.rootFolder,[vim.HostSystem],True)
	hosts=[host for host in host_view.view]
	ping_status=self.ping.verbose_ping(ip)



event_out/get_vm_status.py
    * vnstatus.vnstatus_vm_status 의 상태값과 현재 v-center 에서 vn gueset 의 power 의 상태값 비고
	vm guest 의 power 상태의 변화 에 대한 Event (off-> on , on -> off)


