#!/usr/local/bin/python3.7
# Author: Jagadish.uddandam@oracle.com
# Script to cleanup oracle traces older than 7 days

import subprocess
import sys
import os
import os.path
import time

with open('/etc/oratab','r') as O:
    for line in O.readlines():
        if (line.find('dbhome') != -1):
            O_HOME=line.strip('\n').split(':')[1]
            f=open(f"{O_HOME}/install/orabasetab",'r')
            O_BASE=f.read().split(':')[1]
        elif (line.find('grid') != -1):
            G_HOME=line.strip('\n').split(':')[1]
            h=open(f"{G_HOME}/install/orabasetab",'r')
            G_BASE=h.read().split(':')[1]

command1=f"{G_HOME}/bin/crsctl stat res -w \"TYPE = ora.database.type\" -p |grep -E \"DB_UNIQUE_NAME|USR_ORA_DB_NAME|GEN_USR_ORA_INST_NAME@SERVERNAME\(`hostname`\)\""
pcommand1=subprocess.run([f"{command1}"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,shell=True)
out=pcommand1.stdout.strip().split('\n')
for i in out:
    if i.startswith('DB_UNIQUE'):
        DB_UNIQUE_NAME=i.split('=')[1]
    elif i.startswith('GEN_USR_ORA'):
        INSTANCE_NAME=i.split('=')[1]
    elif i.startswith('USR_ORA'):
        DB_NAME=i.split('=')[1]


print("          INFROMATIONAL ONLY           ")
dash='-' * 80
print(dash)
print(f" DB_UNIQUE_NAME={DB_UNIQUE_NAME}\n INSTANCE_NAME={INSTANCE_NAME}\n DB_NAME={DB_NAME}")
print(dash)

command2=f"{G_HOME}/bin/crsctl stat res -w \"TYPE = ora.asm.type\" -p |grep -E \"GEN_USR_ORA_INST_NAME@SERVERNAME\(`hostname`\)\""
pcommand2=subprocess.run([f"{command2}"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,shell=True)
out2=pcommand2.stdout.strip().split('\n')
for z in out2:
    if z.startswith('GEN_USR'):
        INSTANCE_ASM=z.split('=')[1]

print("===Important Filesystem usage before space clearance==")
p1=subprocess.run(["df","-h"],stdout=subprocess.PIPE,text=True,shell=True)
for i in p1.stdout.split('\n')[1:]:
    j=i.split()[:-3:-1]
    if ("/u01" in j) or ("/" in j):
        print(f"{j[0]} file system is {j[1]} used")

#===Code start for removing tracefiles====

# time is in epoch and removing file older than 7 days

curr = time.time() - (7 * 84500)

#==Removing Oracle Home trace files==
a = os.walk(f"{O_BASE}/diag/rdbms/{DB_UNIQUE_NAME}/{INSTANCE_NAME}/trace")
for i,j,k in a:
    for m in k:
        n=os.path.join(f"{i}",m)
        if os.path.getmtime(n) < curr:
            os.remove(n)
            print("File: ",n,"removed")

#==Removing Grid Home trace files==

b = os.walk(f"{G_BASE}/diag/asm/+asm/{INSTANCE_ASM}/trace")
for i,j,k in b:
    for m in k:
        n=os.path.join(f"{i}",m)
        if os.path.getmtime(n) < curr:
            os.remove(n)
            print("File: ",n,"removed")

print("===Important Filesystem usage After space clearance==")
p2=subprocess.run(["df","-h"],stdout=subprocess.PIPE,text=True,shell=True)
for i in p2.stdout.split('\n')[1:]:
    j=i.split()[:-3:-1]
    if ("/u01" in j) or ("/" in j):
        print(f"{j[0]} file system is {j[1]} used")

