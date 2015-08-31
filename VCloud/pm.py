"""
    VCloud: Virtual Cloud Solutions
    Author: Aaditya M Nair
    Created On: Mon Aug 31 12:28:18 IST 2015

    Handles pm stats.
"""

import libvirt, pymongo
connection = pymongo.MongoClient()
db = connection['VCloud']
phy_mach = db['phy_mach']

def list_pm():
    """
    List all the pms available
    """
    num = phy_mach.count()
    return range(1, num+1)


def list_vm(pmid):
    """
    List all VMs in a PM.
    """
    pm = phy_mach.find_one({'pmid':pmid})
    if pm is None:
        return None
    return pm['vm_id']


def pm_query(pmid):
    """
    List stats about the physical machine.
    """
    ret ={}
    pm = phy_mach.find_one({'pmid':pmid})
    if pm is None:
        return 0

    ret['pmid'] = pmid
    ret['vms'] = pm['vm_count']
    ret['capacity'] = {
            'cpu': pm['available']['vcpu'],
            'ram': pm['available']['memory'],
            'disk':100,
            }
    # TODO: Mon Aug 31 13:14:56 IST 2015 VCPU count ?
    
    conn = libvirt.open(pm['uri'])
    free = conn.getMemoryStats(0)['free']/1024
    conn.close()

    ret['free'] = {
            'cpu': pm['available']['vcpu'],
            'ram':free,
            'disk':50,
            }
    
    return ret

