import get_vm_state
import get_esx_state
import time


while True:
    get_vm_state.VM().main()
    get_esx_state.vm_Perform().main()
    time.sleep(60)
