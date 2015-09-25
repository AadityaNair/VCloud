#!/bin/python
"""
    VCloud: Cloud Deployment
    Author: Aaditya M Nair
    Created On: Fri Sep 25 14:20:24 IST 2015

    This is the main run script for the project.
    -> It establishes keyless-ssh onto various slave systems.
    -> Initialises the database with slave ips and flavors.
    
    Inputs to the file (in order)
    * ips of all slave machines with a single user@ip on each line
    * a list of flavors as found in the flavors file
"""

import sys, os

# Generate SSH keys.
os.system('ssh-keygen -t rsa -f cloud -N "" ')

# install keys in all slave machines.
# ignores if an entry is localhost
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
init_ip(ip_list) # initialise ips into the database.

# directly parse the flavor list as a dictionary.
import ast
flavor_list = open(sys.argv[2]).read().strip().split(':',1)
flavor_list = ast.literal_eval(flavor_list[1])
r={}
counter = 1
# convert the flavor list into a standard form for use by the system.
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
col.insert({'types':r}) # insert into the database

# start the API server
import vcloud
vcloud.app.run(host='0.0.0.0', debug=True, use_reloader=False)
