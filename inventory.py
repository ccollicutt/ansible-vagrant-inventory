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

    # if the cache has been created in the last 24 hours then just use that
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
        # if the host is powered off we can't get ports and such, not sure why
        if host.state != "poweroff":
            port = v.port(vm_name=host.name)
            ip = v.hostname(vm_name=host.name)
            keyfile = v.keyfile(vm_name=host.name)

            inventory['all'].append(host.name)
            inventory['_meta']['hostvars'][host.name] = {}
            inventory['_meta']['hostvars'][host.name]['ansible_ssh_port'] = port
            inventory['_meta']['hostvars'][host.name]['ansible_ssh_host'] = ip
            # seems like newer vagrants are not using the insecure private key
            # like they used to and are setting up individual keys for each host
            inventory['_meta']['hostvars'][host.name]['ansible_ssh_private_key_file'] = keyfile

    with open(INVENTORY_CACHE, 'w') as outfile:
        json.dump(inventory, outfile)

print(json.dumps(inventory, indent=4))
