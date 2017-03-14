#!/usr/bin/python


ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'brian',
                    'version': '1.0'}

DOCUMENTATION = '''
---
module: ucs_vlan_exists
version_added: "2.2"
short_description: Checks existance of Vlans
description:
    - Checks existing of Vlans
author: Jason Barbee (@jasonbarbee)
extends_documentation_fragment: ucs
options:
    vlan_id:
        description:
            - Single VLAN ID.
        required: false
        default: null
'''

from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan
from library.ucs import UCS


def ucs_vlan_exists(module):
    vlan_id = module.params.get('vlan_id')
    ucsm_ip = module.params.get('ip')
    ucsm_pw = module.params.get('password')
    ucsm_login = module.params.get('login')

    ucsm = UCS(ucsm_ip, ucsm_login, ucsm_pw)

    results = {}

    #Login to UCSM
    try:
        ucsm.login()
        results['logged_in'] = True
    except Exception as e:
        module.fail_json(msg=e)

    # Obtain a handle for the LAN Cloud
    lancloud = ucsm.handle.query_classid(class_id="FabricLanCloud") 

    test_vlan = ucsm.handle.query_children(
                in_mo=lancloud[0],
                class_id="FabricVlan",
                filter_str='(id, %s, type="eq")' % (vlan_id)
	 	)
	
    try:
	 if test_vlan[0].id == vlan_id: 
	     module.fail_json(msg="UCS Vlan already exists!")
	     results['existance'] = 'true'
    except Exception as e:
         results['existance'] = 'false'
    try:
        ucsm.handle.logout()
        results['logged_out'] = True
    except Exception as e:
        module.fail_json(msg=e)

    return results

def main():
    module = AnsibleModule(
        argument_spec     = dict(
        vlan_id           = dict(required=False),
        ip                = dict(required=True),
        password          = dict(required=True),
        login             = dict(required=True),
        )
    )



    vlan_id = module.params.get('vlan_id')

    if vlan_id:
        results = ucs_vlan_exists(module)
        module.exit_json(**results)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()


