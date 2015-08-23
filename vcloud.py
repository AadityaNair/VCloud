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

@app.route('/vm/create', methods=['GET', 'POST'])
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
    pass
    
    return flask.jsonify({'vmid':0})

@app.route('/vm/query')
def vm_query():
    vm_id = request.args.get('vmid', None)

    ret={
            'vmid':0,
            'name':"test",
            'instance_type':3,
            'pmid':2,
        }
    return flask.jsonify(ret)

@app.route('/vm/destroy')
def vm_destroy():
    vm_id = request.args.get('vmid', None)
    if vm_id is None:
        flask.abort(400)

    return flask.jsonify({'status':1})

@app.route('/vm/types')
def vm_types():
    """
    Returns a list of all possible types of vm instances that can exist.
    Types include TypeID(tid), CPUs, RAM and DISK.
    """

    inst_types = [{
        'tid':1,
        'cpu':2,
        'ram':512,
        'disk': 1024,
        }]
    return flask.jsonify({'types':inst_types}), 300


# Requests related to information about Physical Machines.
@app.route('/pm/list')
def pm_list():
    """
    Lists all the physical machines available to the app.
    """

    machines = [1, 2, 3]
    return flask.jsonify({'pmids':machines})

@app.route('/pm/<int:pmid>/listvms')
def list_vms(pmid):
    """
    List all the VMs running on a particular physical machine.
    """
    vms = [1, 2, 3]
    return flask.jsonify({'vmids':vms})

@app.route('/pm/<int:pmid>')
def pm_stat(pmid):
    """
    Displays all the stats of the Physical Machine.
    Stats include CPU, RAM and DISK: capacity and free.
    Number of VMs.
    """

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
    app.run(host='0.0.0.0')
