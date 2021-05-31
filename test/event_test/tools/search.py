import glob
import re


tlist=glob.glob('vcenter_evet*.txt')

for t  in tlist:
    with open(t) as f:
        tmp=f.read()
    
    if re.search(tmp,'alarm'):
        print t