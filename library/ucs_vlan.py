#!/usr/bin/python


ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'brian',
                    'version': '1.0'}

DOCUMENTATION = '''
---
module: ucs_vlan
version_added: "2.2"
short_description: Manages VLAN resources additions.
description:
    - Manages VLAN configurations on UCS Manager instances.
author: Brian Hopkins (@br1anhopkins)
extends_documentation_fragment: ucs
options:
    vlan_id:
        description:
            - Single VLAN ID.
        required: false
        default: null
    vlan_name:
        description:
            - Vlan name, include the seperator you want between the name and id.
              Example vlan_ID or vlan-ID.  vlan_id is appended to this value.
        required: true
        default: null
    vlan_range:
        description:
            - Range of vlan's for UCS Cloud VLAN's, not VLAN's configured on FI A and B Seperately.
              Ex. 2-10 will create vlan 2-10 on combined VLAN's section.  For independent LAN config see configure_lan_seperate.
        required: false
        default: null
    configure_lan_seperate:
        description:
            - This flag tells the scripts whether to configure LAN seperate on each FI or to do combined.
        required: false
        default: no
        choices: ['yes', 'no']
    vlan_a_range:
        description:
            - The vlan range for FI A if you have configure_lan_seperate set to yes.
              Ex. 2-10 will create vlan 2-10 on FI A.
        required: false
        default: null
    vlan_b_range:
        description:
            - The vlan range for FI B if you have configure_lan_seperate set to yes.
              Ex. 2-10 will create vlan 2-10 on FI B.
        required: false
        default: null
    policy_owner:
        description:
            - The policy owner value.
        required: true
        default: default
        choices: ['local', 'pending-policy', 'policy']
    mcast_policy_name:
        description:
            - The multicast policy name, varies on your env.
        required: false
        default: null
        choices: ['default', 'your_policy_name']

'''

EXAMPLES = '''
- name: Adding Single Vlan ID {{vlan_id}} {{ucsm_ip}}
    ucs_vlan:
      ip={{ucsm_ip}}
      login={{ucsm_login}}
      password={{ucsm_pw}}
      vlan_name='vlan_'
      vlan_id='10'
      mcast_policy_name=''
      policy_owner='local'

- name: Add Single VLAN Seperate FI A/B {{ ucsm_ip }}
      ucs_vlan:
        ip={{ucsm_ip}}
        login={{ucsm_login}}
        password={{ucsm_pw}}
        vlan_name="vlan_"
        mcast_policy_name="default"
        policy_owner="local"
        configure_lan_seperate='yes'
        vlan_a='199'
        vlan_b='299'

- name: Adding VLAN Range Combined LAN Cloud {{vlan_range}} {{ucsm_ip}}
    ucs_vlan:
      ip={{ucsm_ip}}
      login={{ucsm_login}}
      password={{ucsm_pw}}
      vlan_name='vlan_'
      vlan_range="10-20"
      mcast_policy_name="default"
      policy_owner="local"

- name: Adding VLAN Range FI A/B Seperate {{vlan_a_range}} {{vlan_b_range}} {{ucsm_ip}}
    ucs_vlan:
      ip={{ucsm_ip}}
      login={{ucsm_login}}
      password={{ucsm_pw}}
      vlan_name='vlan_'
      mcast_policy_name="default"
      policy_owner="local"
      configure_lan_seperate="yes"
      vlan_a_range="300-310"
      vlan_b_range="200-210"

'''



from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan
from library.ucs import UCS


def ucs_add_vlan(module):
    vlan_name = module.params.get('vlan_name')
    vlan_id = module.params.get('vlan_id')
    mcast_policy_name = module.params.get('mcast_policy_name')
    policy_owner = module.params.get('policy_owner')
    configure_lan_seperate = module.params.get('configure_lan_seperate')
    vlan_a = module.params.get('vlan_a')
    vlan_b = module.params.get('vlan_b')
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


#
# Checking if configured for lan seperate per FI or not.
#

    if configure_lan_seperate == 'no':
        mo = FabricVlan(parent_mo_or_dn="fabric/lan", sharing="none", name=vlan_name + str(vlan_id), id=vlan_id,
                    mcast_policy_name=mcast_policy_name, policy_owner=policy_owner, default_net="no", pub_nw_name="",
                    compression_type="included")

        try:
            ucsm.handle.add_mo(mo)
            ucsm.handle.commit()
            results['changed'] = True

        except Exception as e:
            module.fail_json(msg=e)
            results['changed'] = False
    else:
        mo = FabricVlan(parent_mo_or_dn="fabric/lan/A", sharing="none", name=vlan_name + str(vlan_a), id=str(vlan_a),
                        mcast_policy_name=mcast_policy_name, policy_owner=policy_owner, default_net="no",
                        pub_nw_name="",
                        compression_type="included")
        ucsm.handle.add_mo(mo)

        mo = FabricVlan(parent_mo_or_dn="fabric/lan/B", sharing="none", name=vlan_name + str(vlan_b), id=str(vlan_b),
                        mcast_policy_name=mcast_policy_name, policy_owner=policy_owner, default_net="no",
                        pub_nw_name="",
                        compression_type="included")

        ucsm.handle.add_mo(mo)

        try:
            ucsm.handle.commit()
            results['changed'] = True

        except Exception as e:
            module.fail_json(msg=e)
            results['changed'] = False

    try:
        ucsm.handle.logout()
        results['logged_out'] = True
    except Exception as e:
        module.fail_json(msg=e)



    return results

def ucs_add_vlan_range(module):
    ucsm_ip = module.params.get('ip')
    ucsm_pw = module.params.get('password')
    ucsm_login = module.params.get('login')
    vlan_name = module.params.get('vlan_name')
    vlan_range = module.params.get('vlan_range')
    mcast_policy_name = module.params.get('mcast_policy_name')
    policy_owner = module.params.get('policy_owner')
    configure_lan_seperate = module.params.get('configure_lan_seperate')
    vlan_a_range = module.params.get('vlan_a_range')
    vlan_b_range = module.params.get('vlan_b_range')

    results = {}

    ucsm = UCS(ucsm_ip, ucsm_login, ucsm_pw)

    results = {}

    # Login to UCSM
    try:
        ucsm.login()
        results['logged_in'] = True
    except Exception as e:
        module.fail_json(msg=e)


    if vlan_range:
        vlan_range_split = vlan_range.split('-')
        vlan_start = int(vlan_range_split[0])
        vlan_end = int(vlan_range_split[1]) + 1
        vlan_list = list(range(vlan_start, vlan_end))


    elif vlan_a_range:
        vlan_a_range_split = vlan_a_range.split('-')
        vlan_a_start = int(vlan_a_range_split[0])
        vlan_a_end = int(vlan_a_range_split[1]) + 1
        vlan_a_list = list(range(vlan_a_start, vlan_a_end))


    if vlan_b_range:
        vlan_b_range_split = vlan_b_range.split('-')
        vlan_b_start = int(vlan_b_range_split[0])
        vlan_b_end = int(vlan_b_range_split[1]) + 1
        vlan_b_list = list(range(vlan_b_start, vlan_b_end))


    if configure_lan_seperate == 'no':

        for vlan in vlan_list:
            mo = FabricVlan(parent_mo_or_dn="fabric/lan", sharing="none", name=vlan_name + str(vlan), id=str(vlan),
                        mcast_policy_name=mcast_policy_name, policy_owner=policy_owner, default_net="no", pub_nw_name="",
                        compression_type="included")
            try:
                ucsm.handle.add_mo(mo)
                results['changed'] = True

            except Exception as e:
                module.fail_json(msg=e)
                results['changed'] = False
    else:

        for vlan in vlan_a_list:
            mo = FabricVlan(parent_mo_or_dn="fabric/lan/A", sharing="none", name=vlan_name + str(vlan), id=str(vlan),
                            mcast_policy_name=mcast_policy_name, policy_owner=policy_owner, default_net="no",
                            pub_nw_name="",
                            compression_type="included")
            try:
                ucsm.handle.add_mo(mo)
                results['changed'] = True


            except Exception as e:
                module.fail_json(msg=e)
                results['changed'] = False

        for vlan in vlan_b_list:
            mo = FabricVlan(parent_mo_or_dn="fabric/lan/B", sharing="none", name=vlan_name + str(vlan), id=str(vlan),
                            mcast_policy_name=mcast_policy_name, policy_owner=policy_owner, default_net="no",
                            pub_nw_name="",
                            compression_type="included")
            try:
                ucsm.handle.add_mo(mo)
                results['changed'] = True

            except Exception as e:
                module.fail_json(msg=e)
                results['changed'] = False

    #Committing Changes
    ucsm.handle.commit()



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
        vlan_id           = dict(required=False),
        mcast_policy_name = dict(required =False),
        policy_owner      = dict(defualt = 'local', choices = ['local', 'pending-policy', 'policy']),
        configure_lan_seperate=dict(required=False, default='no', choices=['yes', 'no']),
        vlan_a            = dict(required=False),
        vlan_b            = dict(required=False),
        ip                = dict(required=True),
        password          = dict(required=True),
        login             = dict(required=True),
        vlan_range=dict(required=False),
        vlan_a_range=dict(required=False),
        vlan_b_range=dict(required=False)
        )
    )



    vlan_id = module.params.get('vlan_id')
    vlan_a_range = module.params.get('vlan_a_range')
    vlan_range = module.params.get('vlan_range')
    vlan_a = module.params.get('vlan_a')

    if vlan_id:
        results = ucs_add_vlan(module)
        module.exit_json(**results)

    elif vlan_a_range:
        results = ucs_add_vlan_range(module)
        module.exit_json(**results)

    elif vlan_range:
        results = ucs_add_vlan_range(module)
        module.exit_json(**results)

    elif vlan_a:
        results = ucs_add_vlan(module)
        module.exit_json(**results)

    else:
        module.fail_json(msg='Missing either vlan_id or vlan_a/b_range')






from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()