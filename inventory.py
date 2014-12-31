#!/usr/bin/python

import vagrant
import json
import os
import sys
import time

INVENTORY_CACHE="inventory-cache.json"

inventory = None

if os.path.isfile(INVENTORY_CACHE):

    mtime = os.path.getmtime(INVENTORY_CACHE)
    yesterday = time.time() - (60*60*24)

    
    if mtime > yesterday:
        with open(INVENTORY_CACHE) as inventory_json:
            inventory = json.load(inventory_json)

if inventory == None:
    v = vagrant.Vagrant()
    hosts = v.status()
    grp = {}
    group = "all"
    grp[group] = []

    inventory = {}
    inventory['_meta'] = { 'hostvars': {} }
    inventory['all'] = []

    for host in hosts:
        inventory['all'].append(host.name)

        inventory['_meta']['hostvars'][host.name] = {}
        inventory['_meta']['hostvars'][host.name]['ansible_ssh_port'] = \
        v.port(vm_name=host.name)
        inventory['_meta']['hostvars'][host.name]['ansible_ssh_host'] = \
        v.hostname(vm_name=host.name)
        inventory['_meta']['hostvars'][host.name]['ansible_ssh_private_key_file'] \
        = v.keyfile(vm_name=host.name)

    with open(INVENTORY_CACHE, 'w') as outfile:
        json.dump(inventory, outfile)

print(json.dumps(inventory, indent=4))
