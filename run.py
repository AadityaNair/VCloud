#!/bin/python

import sys, os

os.system('ssh-keygen -t rsa -f cloud -N "" ')

ip_list = []
with open(sys.argv[1]) as f:
    for line in f:
        line = line.strip()
        print line
        ip_list.append(line)
        if line != '127.0.0.1':
            cmd = "ssh-copy-id -i cloud "+line
            os.system(cmd)
        else:
            print "Localhost"
os.system("ssh-add cloud")

from VCloud.initialise import init_ip
init_ip(ip_list)

import ast
flavor_list = open(sys.argv[2]).read().strip().split(':',1)
flavor_list = ast.literal_eval(flavor_list[1])
r={}
counter = 1
for flavor in flavor_list:
    a=[]
    a.append( ('{{memory}}', flavor['ram']) )
    a.append( ('{{vcpu}}', flavor['cpu']) )
    r[str(counter)] = a
    counter +=1

import pymongo
conn = pymongo.MongoClient()
db = conn.VCloud
col = db.flavors
col.insert({'types':r})

import vcloud
vcloud.app.run(host='0.0.0.0', debug=True, use_reloader=False)
