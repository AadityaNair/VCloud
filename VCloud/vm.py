"""
    VCloud : Cloud Setup Solutions
    Author: Aaditya M Nair
    Created On: Sun Aug 30 18:41:10 IST 2015

    This module deals with creation, deletion and query of 
    Virtual Machines.
"""

import libvirt, pymongo
connection = pymongo.MongoClient()
db = connection['VCloud']
# TODO: Mon Aug 31 01:29:05 IST 2015 Better instance Handling.
instances = {
        1: [
            ('{{memory}}', 1024),
            ('{{vcpu}}', 1),
            ],
        2: [
            ('{{memory}}', 2048),
            ('{{vcpu}}', 2),
            ]
        }

def find_best(mem):
    """
    Find the best pm from the available ones.
    Presently it is the first one that has enough memory.
    """
    phy_mach = db['phy_mach']
    sel = db.find_one()

    for machine in phy_mach.find():
        conn = libvirt.open(machine['uri'])
        mem_stat = conn.getMemoryStats(0)
        if mem_stat['free'] > mem:
            return conn, machine



def create(name, inst_type):
    """
    Create a virtual machine based on instance type.
    """
    XmlDesc = open('./templates/vm_template.xml').read()
    XmlDesc = XmlDesc.replace('{{name}}', name)
    rep = instances[inst_type] 
    # TODO: Sun Aug 30 19:07:44 IST 2015 Error Checking

    for tuple in rep: # create the XML
       XmlDesc = XmlDesc.replace(tuple[0], str(tuple[1]))
    ram_req = rep[0][1]

    # query the physical machine
    conn, machine = find_best(ram_req)
    dom=conn.createXML(xml)
    machine['vm_count'] += 1

    vmid = str(machine[pmid])+'pv'+str(dom.ID())
    machine['vm_id'].append(vmid)

    pm = db['phy_mach']
    pm.update({'_id':machine['_id']}, {'$set':machine}, upsert=False)
    conn.close()


def query(id):
    """
    Queries various stats about the vmid specified.
    """
    pmid, vmid = id.split('pv')
    pm_list = db['phy_mach']
    pm = pm_list.find_one({'pmid':pmid})

    conn = libvirt.open(pm['uri'])
    dom = conn.lookupByID(vmid)
# TODO: Mon Aug 31 01:34:01 IST 2015 error handling
    name , inst_type = dom.name() int(dom.maxMemory()/(1024*1024))
    conn.close()
    return pmid, vmid, name, inst_type

def destroy(id):
    """
    Destroys the vmid provided.
    """
    pmid, vmid = id.split('pv')
    pm_list = db['phy_mach']
    pm = pm_list.find_one({'pmid':pmid})

    conn = libvirt.open(pm['uri'])
    dom = conn.lookupByID(vmid)
    dom.destroy()

    pm['vm_count'] -=1
    pm['vm_id'].remove(id)
    pm_list.update({'_id':pm['_id']}, {'$set':pm}, upsert=False)
    conn.close()
    return 0

def types():
    """
    Return VM instance types.
    """
    ret = []

    for key, value in instances:
        d = {}
        d['tid'] = key
        d['ram'] = value[0][1]
        d['cpu'] = value[1][1]
        d['disk'] = 3

        ret.append(d)
    return d
