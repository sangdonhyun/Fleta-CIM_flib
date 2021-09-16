import re
with open('result.txt') as f:
    lineset= f.read().split(',')

with open('value.txt') as f:
    vlineset= f.read().split(',')


print (len(lineset)),(len(vlineset))

with open('esxtop.txt','w') as f:
    with open('cpu.txt','w') as fcpu:
        for i in range(len(lineset)):

            f.write("{} {}\n".format(lineset[i], vlineset[i]))

            if 'Group Cpu' in lineset[i] and 'Ready' in lineset[i]:
                print lineset[i], vlineset[i]
                fcpu.write("{} {}\n".format(lineset[i], vlineset[i]))