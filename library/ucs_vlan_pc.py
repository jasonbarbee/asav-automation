#!/usr/bin/python

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'Jason Barbee',
                    'version': '0.1'}

DOCUMENTATION = '''
---
module: ucs_vlan_to_pc
version_added: "2.2"
short_description: Adds Vlan to Port Channels. Name and ID must match exactly
description:
    - Adds or removes Vlans from Port Channels. Name and ID must match exactly
author: Jason Barbee (@jasonbarbee)
extends_documentation_fragment: ucs
options:
    vlan_id:
        description:
            - Single VLAN ID.
        required: false
        default: null
    pc_id:
        description:
            - Port Channel ID
        required: false
        default: null
    vlan_name:
        description:
            - Vlan name, include the seperator you want between the name and id.
              Example vlan_ID or vlan-ID.  vlan_id is appended to this value.
        required: true
        default: null
    vlan_name:
        description:
            - admin speed. 1gbps 10gbps or 40gpbs
        required: false
        default: 10gbps
    state:
        description:
        - Desired State of the action - present / absent
        required: true
        default: true
        choices ['True','False']
'''

EXAMPLES = '''
- name: Adding Single Vlan ID {{vlan_id}} to {{ pc_id} on UCS:{{ucsm_ip}}
    ucs_vlan_add_to_pc:
      ip={{ucsm_ip}}
      login={{ucsm_login}}
      password={{ucsm_pw}}
      vlan_name='vlan_'
      vlan_id='10'
      pc_id='1'

- name: Adding Single Vlan ID {{vlan_id}} to {{ pc_id} on UCS:{{ucsm_ip}}
    ucs_vlan_remove_from_pc:
      ip={{ucsm_ip}}
      login={{ucsm_login}}
      password={{ucsm_pw}}
      vlan_name='servers'
      vlan_id='10'
      pc_id='1'
'''



from ucsmsdk.mometa.fabric.FabricEthLan import FabricEthLan
from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan
from ucsmsdk.mometa.fabric.FabricEthVlanPc import FabricEthVlanPc
from library.ucs import UCS


def ucs_add_vlan_to_pc(module):
    vlan_name = module.params.get('vlan_name')
    vlan_id = module.params.get('vlan_id')
    ucsm_ip = module.params.get('ip')
    ucsm_pw = module.params.get('password')
    ucsm_login = module.params.get('login')
    pc_id = module.params.get('pc_id')
    admin_speed = module.params.get('admin_speed')
    is_native = module.params.get('is_native')

    ucsm = UCS(ucsm_ip, ucsm_login, ucsm_pw)

    results = {}

    #Login to UCSM
    try:
        ucsm.login()
        results['logged_in'] = True
    except Exception as e:
        module.fail_json(msg=e)

    FILIST = ['A', 'B']
    for FI in FILIST:
        obj = ucsm.handle.query_dn("fabric/lan")
	# Attaches a single Global Vlan to Port Channel
        try:
#            mo = FabricEthLan(parent_mo_or_dn=obj, id=FI)
            mo_1 = FabricVlan(parent_mo_or_dn=obj, sharing="none", name=vlan_name, id=vlan_id, mcast_policy_name="", policy_owner="local", default_net="no", pub_nw_name="", compression_type="included")
            mo_1_1 = FabricEthVlanPc(parent_mo_or_dn=mo_1, name="", descr="", is_native=is_native, admin_speed=admin_speed, switch_id=FI, admin_state="enabled", oper_speed=admin_speed, port_id=pc_id)
            ucsm.handle.add_mo(mo_1, modify_present=True)

            ucsm.handle.commit()
            results['changed'] = True

        except Exception as e:
                results['changed'] = False
                try:
                    ucsm.handle.logout()
                    results['logged_out'] = True
                except Exception as e:
                    module.fail_json(msg=e)

    try:
        ucsm.handle.logout()
        results['logged_out'] = True
    except Exception as e:
        module.fail_json(msg=e)

    return results

def ucs_remove_vlan_from_pc(module):
    vlan_name = module.params.get('vlan_name')
    vlan_id = module.params.get('vlan_id')
    ucsm_ip = module.params.get('ip')
    ucsm_pw = module.params.get('password')
    ucsm_login = module.params.get('login')
    pc_id = module.params.get('pc_id')
    admin_speed = module.params.get('admin_speed')
    is_native = module.params.get('is_native')

    ucsm = UCS(ucsm_ip, ucsm_login, ucsm_pw)

    results = {}

    #Login to UCSM
    try:
        ucsm.login()
        results['logged_in'] = True
    except Exception as e:
        module.fail_json(msg=e)

    FILIST = ['A','B']
    for FI in FILIST:
        obj = ucsm.handle.query_dn("fabric/lan")
        lancloud = ucsm.handle.query_classid(class_id="FabricLanCloud") 
        try:
            mo = FabricEthLan(parent_mo_or_dn=obj, id=FI)
            mo_1 = FabricVlan(parent_mo_or_dn=mo, sharing="none", name=vlan_name, id=vlan_id, mcast_policy_name="", policy_owner="local", default_net="no", pub_nw_name="", compression_type="included")
            mo_1_1 = ucsm.handle.query_children(
                in_mo=mo_1,
                class_id="FabricEthVlanPc",
                filter_str='(vlan_name + + str(vlan_id), %s, type="eq")' % (vlan_name,vlan_id)
    	 	)  
            #mo_1_1 = FabricEthVlanPc(parent_mo_or_dn=mo_1, name=vlan_name + + str(vlan_id), descr="", is_native=is_native, admin_speed=admin_speed, switch_id=FI, admin_state="enabled", oper_speed=admin_speed, port_id=pc_id)

            ucsm.handle.remove_mo(mo_1_1)
            ucsm.handle.commit()
            results['changed'] = True

        except Exception as e:
                results['changed'] = False
                try:
                    ucsm.handle.logout()
                    results['logged_out'] = True
                except Exception as e:
                    module.fail_json(msg=e)

    try:
        ucsm.handle.logout()
        results['logged_out'] = True
    except Exception as e:
        module.fail_json(msg=e)

    return results

def main():
    module = AnsibleModule(
        argument_spec     = dict(
        pc_id             = dict(required=True),
        vlan_id           = dict(required=True),
        vlan_name         = dict(required=True),
        ip                = dict(required=True),
        password          = dict(required=True),
        login             = dict(required=True),
        admin_speed       = dict(required=False, default='10gbps'),
        is_native         = dict(required=False),
    	state 		      = dict(required=False, default='present',choices=['present', 'absent']),
        )
    )

    vlan_id = module.params.get('vlan_id')
    pc_id = module.params.get('pc_id')
    state = module.params.get('state')
    vlan_name = module.params.get('vlan_name')

    if pc_id:
        if state == 'present':
            if len(vlan_name) <= 32:
                results = ucs_add_vlan_to_pc(module)
                module.exit_json(**results)
            else:
                module.fail_json(msg='Vlan Name must be 32 char or less')
        else:
                results = ucs_remove_vlan_from_pc(module)
                module.exit_json(**results)
    else:
        module.fail_json(msg='Missing port channel id.')


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
