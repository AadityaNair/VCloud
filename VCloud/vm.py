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
pm = db.phy_mach
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
    # TODO: Mon Aug 31 13:42:51 IST 2015 Check VCPU
    sel = pm.find_one()

    for machine in pm.find():
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
    
    try:
        rep = instances[inst_type]
    except KeyError:
        return 0, "Wrong instance instance type"

    for tuple in rep: # create the XML
       XmlDesc = XmlDesc.replace(tuple[0], str(tuple[1]))
    ram_req = rep[0][1]

    # query the physical machine

    try:
        conn, machine = find_best(ram_req)
        dom=conn.createXML(xml)
    except:
        return 0, "Unable to create VM."
    
    machine['vm_count'] += 1

    vmid = str(machine[pmid])+'pv'+str(dom.ID())
    machine['vm_id'].append(vmid)

    pm.update({'_id':machine['_id']}, {'$set':machine}, upsert=False)
    conn.close()
    return vmid, None


def query(id):
    """
    Queries various stats about the vmid specified.
    """
    pmid, vmid = id.split('pv')
    
    machine = pm.find_one({'pmid':pmid})
    if machine is None:
        return 0, None, None, None, "Wrong pmid"
    conn = libvirt.open(machine['uri'])
    
    try:
        dom = conn.lookupByID(vmid)
    except libvirt.libvirtError
        return pmid, 0, None, None, "Incorrect vmid."

    name , inst_type = dom.name() int(dom.maxMemory()/(1024*1024))
    conn.close()
    return pmid, vmid, name, inst_type, None

def destroy(id):
    """
    Destroys the vmid provided.
    """
    pmid, vmid = id.split('pv')
    machine = pm.find_one({'pmid':pmid})
    if machine is None:
        return 0, "Wrong pmid"
    conn = libvirt.open(machine['uri'])
    try:
        dom = conn.lookupByID(vmid)
    except libvirt.libvirtError:
        return 0, "wrong vmid"
    dom.destroy()
    # TODO: Mon Aug 31 19:31:15 IST 2015 what if destroy doesn't work.

    machine['vm_count'] -=1
    machine['vm_id'].remove(id)
    pm.update({'_id':machine['_id']}, {'$set':machine}, upsert=False)
    conn.close()
    return 1, None

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
