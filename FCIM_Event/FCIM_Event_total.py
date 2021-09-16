import get_esx_state
import get_vm_state
import vcenter_alarm
import vcenter_event
import vcenter_health_vm
import vcenter_health_host
import time


while True:
    try:
        get_esx_state.vm_Perform().main()
    except:
        pass
    print '-' * 50
    try:
        get_vm_state.VM().main()
    except:
        pass
    print '-' * 50
    try:
        vcenter_alarm.vcEvent().main()
    except:
        pass
    print '-' * 50
    try:
        vcenter_event.Manager().main()
    except:
        pass
    print '-' * 50
    try:
        vcenter_health_host.Manager().main()
    except:
        pass
    print '-' * 50
    try:
        vcenter_health_vm.Manager().main()
    except:
        pass
    print '-' *50
    print 'time sleep 60 sec'
    time.sleep(60)
