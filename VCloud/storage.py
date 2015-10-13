"""
    VCloud: Cloud Deployment
    Author: Aaditya M Nair
    Created On: Sun Oct 11 01:45:07 IST 2015

    Defines storage and stuff.
"""

import rados, rbd, libvirt
pool_name = 'vcloud'

cluster = rados.Rados(conffile='/home/Aaditya/projects/VCloud/files/ceph.conf')
cluster.connect()
try:
    cluster.create_pool(pool_name)
except rados.ObjectExists:
    print "Pool exists"
    pass
ioctx = cluster.open_ioctx(pool_name)
storage = rbd.RBD()

import pymongo
conn = pymongo.MongoClient()
db = conn.VCloud

pm = db.phy_mach
store = db.storage

def create_volume(name, size):
    try:
        name = str(name)
        size = int(size)
    except:
        return -1

    try:
        storage.create(ioctx, name, size*(1024**3))
    except:
        return -1
    data={
            'name':name,
            'size':size,
            'vmid':0,
        }
    store.insert(data)
    return 0

def delete_volume(name):
    name = str(name)
    ret = store.find_one({'name':name})
    if ret == None:
        return 0
    store.delete_one({'name':name})
    try:
        storage.remove(ioctx, name)
    except:
        return 0
    return 1

def query_volume(name):
    name = str(name)
    data = store.find_one({'name':name})
    if data is None:
        return None
    return  (data['name'], data['size'], data['vmid'])

def attach_volume(vm, volumeid):
    volumeid = str(volumeid)
    try:
        pmid, vmid = vm.split('pv')
        pmid, vmid = int(pmid), int(vmid)
    except:
        print "wrong ids"
        return 0
    data = store.find_one({'name':volumeid})
    if data is None:
        print "no such volume"
        return 0
    if data['vmid']!=0:
        print "already attached"
        return 0
    
    machine = pm.find_one({'pmid':pmid})
    try:
        machine['vm_id'].index(vm)
    except:
        print "no such vm"
        return 0


    command = 'sudo rbd map '+volumeid+' --pool '+pool_name+' -c /home/Aaditya/projects/VCloud/files/ceph.conf'
    import os
    retval = os.system(command)
    if retval != 0:
        print "map failed"
        return 0


    conn = libvirt.open(machine['uri'])
    dom = conn.lookupByID(vmid)

    disk=open('/home/Aaditya/projects/VCloud/VCloud/templates/disk.xml').read()
    disk=disk.replace('{{pool_name}}', pool_name).replace('{{volume}}', volumeid)
    
    try:
        dom.attachDevice(disk)
    except:
        print "attach failed"
        return 0
    data['vmid']=vm
    store.update({'_id':data['_id']}, {'$set':data}, upsert=False)
    return 1


def detach_volume(volumeid):
    volumeid = str(volumeid)
    
    data= store.find_one({'name':volumeid})
    if data is None or data['vmid'] == 0:
        print "no such volume or already detached"
        return 0

    vm = data['vmid']
    pmid, vmid = vm.split('pv')
    pmid, vmid = int(pmid), int(vmid)
    
    machine = pm.find_one({'pmid':pmid})
    
    conn = libvirt.open(machine['uri'])
    dom = conn.lookupByID(vmid)
    disk=open('/home/Aaditya/projects/VCloud/VCloud/templates/disk.xml').read()
    disk=disk.replace('{{pool_name}}', pool_name).replace('{{volume}}', volumeid)
    
    try:
        dom.detachDevice(disk)
    except:
        print "detach failed"
        return 0
    print "detach successful"
    dom.reboot()

    command = 'sudo rbd unmap /dev/rbd/'+pool_name+'/'+volumeid
    import os
    retval = os.system(command)
    if retval != 0:
        print "unmap failed"
        return 0

    data['vmid']=0
    store.update({'_id':data['_id']}, {'$set':data}, upsert=False)
    return 1


