'''
Created on 2019. 6. 4.

@author: Administrator
'''


import os


with open('vcenter_evet.txt') as f:
    tmp = f.readlines()
    
    
for line in tmp:
    if 'fullFormattedMessage' in line:
        print line
        