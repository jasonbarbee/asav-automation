#!/usr/bin/python
# TODO Error handling.
# Detect parameters missing. Ansible does this right?...
# Merge add/remove

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'Jason Barbee',
                    'version': '0.1'}

DOCUMENTATION = '''
---
module: ucs_vlan_vnic
version_added: "2.2"
short_description: Adds Vlan to VNIC Template. Vlan Name must match exactly
description:
    - Adds Vlan to VNIC Template. Vlan Name must match exactly
author: Jason Barbee (@jasonbarbee)
extends_documentation_fragment: ucs
options:
    vnic_template:
        description:
            - Single VNIC Template Name
        required: true
        default: null
    vlan_name:
        description:
            - Vlan name
        required: true
        default: null
    state:
        description:
        - Desired State of the action - present / absent
        required: true
        default: true
        choices ['True','False']
'''

EXAMPLES = '''
- name: Adding Single Vlan ID to Template
    ucs_vlan_add_to_vnic:
      ip={{ucsm_ip}}
      login={{ucsm_login}}
      password={{ucsm_pw}}
      vlan_name=''
      vnic_template:'vnic-template'

- name: Remove Single Vlan ID to Template
    ucs_vlan_remove_from_vnic:
      ip={{ucsm_ip}}
      login={{ucsm_login}}
      password={{ucsm_pw}}
      vlan_name='servers'
      vnic_template:'vnic-template'
'''

from ucsmsdk.mometa.vnic.VnicLanConnTempl import VnicLanConnTempl
from ucsmsdk.mometa.vnic.VnicEtherIf import VnicEtherIf
from ucsmsdk.mometa.fabric.FabricEthLan import FabricEthLan
from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan

from library.ucs import UCS


def ucs_add_vlan_to_vnic(module):
    vlan_name = module.params.get('vlan_name')
    ucsm_ip = module.params.get('ip')
    ucsm_pw = module.params.get('password')
    ucsm_login = module.params.get('login')
    vnic_template = module.params.get('vnic_template')
    default_net = module.params.get('default_net')

    ucsm = UCS(ucsm_ip, ucsm_login, ucsm_pw)

    results = {}

    #Login to UCSM
    try:
        ucsm.login()
        results['logged_in'] = True
    except Exception as e:
        module.fail_json(msg=e)

    FILIST = ['A']
    for FI in FILIST:
        try:
            obj = ucsm.handle.query_dn("org-root/lan-conn-templ-"+vnic_template)
            mo_1 = VnicEtherIf(parent_mo_or_dn=obj, switch_id='dual', default_net=default_net, name=vlan_name)
            ucsm.handle.add_mo(mo_1, True)
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

def ucs_remove_vlan_from_vnic(module):
    vlan_name = module.params.get('vlan_name')
    ucsm_ip = module.params.get('ip')
    ucsm_pw = module.params.get('password')
    ucsm_login = module.params.get('login')
    vnic_template = module.params.get('vnic_template')
    ucsm = UCS(ucsm_ip, ucsm_login, ucsm_pw)

    results = {}

    #Login to UCSM
    try:
        ucsm.login()
        results['logged_in'] = True
    except Exception as e:
        module.fail_json(msg=e)

    FILIST = ['A']
    for FI in FILIST:
        try:
            mo_1 = ucsm.handle.query_dn("org-root/lan-conn-templ-"+vnic_template+"/if-"+vlan_name)
            ucsm.handle.remove_mo(mo_1, False)
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
        vlan_name         = dict(required=True),
        ip                = dict(required=True),
        password          = dict(required=True),
        login             = dict(required=True),
        vnic_template     = dict(required=True),
        default_net       = dict(required=False, default='no', choices=['yes','no']),
    	state 		      = dict(required=False, default='present',choices=['present', 'absent']),
        )
    )

    state = module.params.get('state')
    vlan_name = module.params.get('vlan_name')

    if vlan_name:
        if state == 'present':
            if len(vlan_name) <= 32:
                results = ucs_add_vlan_to_vnic(module)
            else:
                module.fail_json(msg='Vlan Name must be 32 char or less')
        else:
                results = ucs_remove_vlan_from_vnic(module)
        module.exit_json(**results)
    else:
        module.fail_json(msg='Missing vlan name.')


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
