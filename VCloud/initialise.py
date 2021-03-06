"""
    VCloud: Virtual Cloud Solution
    Author: Aaditya M Nair
    Created On: Mon Aug 24 01:18:22 IST 2015

    This file initialises the whole cloud.
    This file should run before any request can be served.

"""
# TODO: Mon Aug 24 01:22:08 IST 2015 Initialise Network.

import pymongo, libvirt
connection = pymongo.MongoClient('mongodb://localhost:27017/')
db = connection['VCloud']
import os
print os.getcwd()

def init_ip(list_of_ips):
    """
    Initialises the list of ips into the database.
    and get the physical stats about the system.
    """
    pms = db['phy_mach']

    data = []
    id_counter = 1

    for ip in list_of_ips:
        info = {}

        info['pmid'] = id_counter
        info['vm_count'] = 0
        info['vm_id'] = []
        info['ip'] = ip
        info['uri'] = 'qemu+ssh://'+str(ip)+'/system'
        if ip == '127.0.0.1':
            info['uri'] = 'qemu:///system'
        available = info['available'] = {}
        free = info['free'] = {}
        # TODO: Sun Aug 30 03:32:25 IST 2015 Error Handling.
        conn = libvirt.open(info['uri'])
        available['vcpu'] = free['vcpu'] = conn.getMaxVcpus(None)
        
        mem = conn.getMemoryStats(0) # Returns memory in KiB
        available['memory'] = mem['total']/1024
        
        data.append(info)
        conn.close()
        id_counter += 1
    
    pms.insert(data)

def init_storage():
    pass

def init_network():
    pass
