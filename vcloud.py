"""
    VCloud: Virtual Cloud Solution
    Author: Aaditya M Nair
    Created On: Sun Aug 23 20:40:24 IST 2015

    Main RESTful server.
    Recieves all requests and sends to LibVirt
"""

import flask
from flask import request

app = flask.Flask(__name__)

@app.route('/')
def hello():
    return "Hello World"


# Requests related to VM creation, deletion and types.

@app.route('/vm/create')
def vm_create():
    """
    Used to create a VM.
    arguements: vmName, InstanceType
    returns   : vmID(if successful), 0(otherwise)
    """
    vm_name = request.args.get('name', None)
    vm_type = request.args.get('instance_type', None)
    if vm_name is None or vm_type is None:
        flask.abort(400)
    
    from VCloud.vm import create
    vmid, msg = create(vm_name, vm_type)
    
    if vmid == 0:
        return flask.jsonify({'vmid':0, 'Error': msg})
    return flask.jsonify({'vmid':vmid})

@app.route('/vm/query')
def vm_query():
    id = request.args.get('vmid', None)
    if id is None:
        flask.abort(400)

    from VCloud.vm import query
    pmid, vmid, name, inst_type, mesg = query(id)

    if pmid == 0 or vmid == 0:
        return flask.jsonify({'Error':mesg})
    else:
        ret={
            'vmid':vmid,
            'name':name,
            'instance_type':inst_type,
            'pmid':pmid,
            }
        return flask.jsonify(ret)

@app.route('/vm/destroy')
def vm_destroy():
    vm_id = request.args.get('vmid', None)
    if vm_id is None:
        flask.abort(400)
    
    from VCloud.vm import destroy
    status, msg = destroy(vm_id)
    if msg is None:
        return flask.jsonify({'status':status})
    else:
        return flask.jsonify({'status':status, 'Error':msg})


@app.route('/vm/types')
def vm_types():
    """
    Returns a list of all possible types of vm instances that can exist.
    Types include TypeID(tid), CPUs, RAM and DISK.
    inst_types = [{
        'tid':1,
        'cpu':2,
        'ram':512,
        'disk': 1024,
        }]
    """
    from VCloud.vm import types
    return flask.jsonify({'types':types()})


# Requests related to information about Physical Machines.
@app.route('/pm/list')
def pm_list():
    """
    Lists all the physical machines available to the app.
    """
    from VCloud.pm import list_pm
    machines = list_pm()
    return flask.jsonify({'pmids':machines})

@app.route('/pm/<int:pmid>/listvms')
def list_vms(pmid):
    """
    List all the VMs running on a particular physical machine.
    """
    from VCloud.pm import list_vm
    vms = list_vm(pmid)
    if vms is None:
        return flask.jsonify({'vmids':'0', 'Error':'Wrong pmid.'})
    return flask.jsonify({'vmids':vms})

@app.route('/pm/<int:pmid>')
def pm_stat(pmid):
    """
    Displays all the stats of the Physical Machine.
    Stats include CPU, RAM and DISK: capacity and free.
    Number of VMs.
    ret = {
            'pmid':pmid,
            'capacity':{
                'cpu':4,
                'ram':4096,
                'disk':160,
                },
            'free':{
                'cpu':4,
                'ram':4096,
                'disk':160,
                },
            'vms':3,
            }
    """
    from VCloud.pm import pm_query
    ret = pm_query(pmid)
    if ret == 0:
        return flask.jsonify({'pmid':0, 'Error':'Wrong pmid'})
    return flask.jsonify(ret)

# requests related to installation images

@app.route('/image/list')
def image_list():
    """
    Lists all the images availabe for installation.
    """

    img = [
            {
                'id':100,
                'name':'Fedora22',
            }
        ]
    return flask.jsonify({'images':img})

if __name__ == '__main__':
    # from VCloud.initialise import init_ip
    # init_ip(['127.0.0.1'])
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
