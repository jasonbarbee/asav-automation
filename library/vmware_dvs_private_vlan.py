#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# Minor change by Jason Barbee 
# Added security policy support - allow mac changes, forged transmits, promiscuous parameters.

# (c) 2015, Joseph Callen <jcallen () csc.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: vmware_dvs_portgroup
short_description: Create or remove a Distributed vSwitch portgroup
description:
    - Create or remove a Distributed vSwitch portgroup
version_added: 2.0
author: "Joseph Callen (@jcpowermac)"
notes:
    - Tested on vSphere 5.5
requirements:
    - "python >= 2.6"
    - PyVmomi
options:
    portgroup_name:
        description:
            - The name of the portgroup that is to be created or deleted
        required: True
    switch_name:
        description:
            - The name of the distributed vSwitch the port group should be created on.
        required: True
    vlan_id:
        description:
            - The VLAN ID that should be configured with the portgroup
        required: True
    num_ports:
        description:
            - The number of ports the portgroup should contain
        required: True
    portgroup_type:
        description:
            - See VMware KB 1022312 regarding portgroup types
        required: True
        choices:
            - 'earlyBinding'
            - 'lateBinding'
            - 'ephemeral'
    allow_mac_changes:
        description:
            - Sets the Security policy for the port group - Allow Mac Changes
        required: False
        choices:
            - True
            - False
    allow_forged_transmits:
        description:
            - Sets the Security policy for the port group - Allow Forged Transmits
        required: False
        choices:
            - True
            - False
    allow_promiscuous:
        description:
            - Sets the Security policy for the port group - Allow Promiscuous
        required: False
        choices:
            - True
            - False

extends_documentation_fragment: vmware.documentation
'''

EXAMPLES = '''
   - name: Create Management portgroup
     local_action:
        module: vmware_dvs_portgroup
        hostname: vcenter_ip_or_hostname
        username: vcenter_username
        password: vcenter_password
        portgroup_name: Management
        switch_name: dvSwitch
        vlan_id: 123
        num_ports: 120
        portgroup_type: earlyBinding
        state: present
'''

try:
    from pyVmomi import vim, vmodl
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


class VMwareDvsPortgroup(object):
    def __init__(self, module):
        self.module = module
        self.switch_name = self.module.params['switch_name']
        self.public_vlan_id = self.module.params['public_vlan_id']
        self.private_vlan_id = self.module.params['private_vlan_id']
        self.allow_mac_changes = self.module.params['allow_mac_changes']
        self.allow_forged_transmits = self.module.params['allow_forged_transmits']
        self.allow_promiscuous = self.module.params['allow_promiscuous']
        self.dv_switch = None
        self.state = self.module.params['state']
        self.content = connect_to_api(module)

    def process_state(self):
        try:
            dvspg_states = {
                'absent': {
                    'present': self.state_destroy_private_vlan,
                    'absent': self.state_exit_unchanged,
                },
                'present': {
                    'update': self.state_update_dvspg,
                    'present': self.state_exit_unchanged,
                    'absent': self.state_create_dvspg,
                }
            }
            dvspg_states[self.state][self.check_dvspg_state()]()
	# This didn't work here either.
        except vim.fault.NotFound as notfound_fault:
            self.module.fail_json(msg=str("Vlan Not Found!"))
        except vmodl.RuntimeFault as runtime_fault:
            self.module.fail_json(msg=runtime_fault.msg)
        except vmodl.MethodFault as method_fault:
            self.module.fail_json(msg=method_fault.msg)
        except Exception as e:
            self.module.fail_json(msg=str(e))

    def create_port_group(self):
        config = vim.VMwareDVSConfigSpec()
	private_vlan_config = []
	#  pvlan_map_entry = vim.dvs.VmwareDistributedVirtualSwitch.PvlanMapEntry()
	#  pvlan_config_spec = vim.dvs.VmwareDistributedVirtualSwitch.PvlanConfigSpec()
	#  pvlan_map_entry.primaryVlanId = pvlan_idx
	#  pvlan_map_entry.secondaryVlanId = pvlan_idx
	#  pvlan_map_entry.pvlanType = "promiscuous"
	#  pvlan_config_spec.pvlanEntry = pvlan_map_entry
	#  pvlan_config_spec.operation = vim.ConfigSpecOperation.add
        # Primary
        pvlan = vim.dvs.VmwareDistributedVirtualSwitch.PvlanConfigSpec() 
        pvlan.operation = vim.ConfigSpecOperation.add
        pvlan.pvlanEntry = vim.dvs.VmwareDistributedVirtualSwitch.PvlanMapEntry() 
        pvlan.pvlanEntry.primaryVlanId = self.public_vlan_id 
        pvlan.pvlanEntry.pvlanType = vim.VmwareDistributedVirtualSwitchPvlanPortType.promiscuous 
        pvlan.pvlanEntry.secondaryVlanId =  self.public_vlan_id
	private_vlan_config.append(pvlan)

        pvlan = vim.dvs.VmwareDistributedVirtualSwitch.PvlanConfigSpec() 
        pvlan.operation = vim.ConfigSpecOperation.add
        pvlan.pvlanEntry = vim.dvs.VmwareDistributedVirtualSwitch.PvlanMapEntry() 
        pvlan.pvlanEntry.primaryVlanId = self.public_vlan_id 
        pvlan.pvlanEntry.pvlanType = vim.VmwareDistributedVirtualSwitchPvlanPortType.community
        pvlan.pvlanEntry.secondaryVlanId = self.private_vlan_id
        private_vlan_config.append(pvlan)
	
	config.pvlanConfigSpec = private_vlan_config
	config.configVersion = self.dv_switch.config.configVersion
        task = self.dv_switch.ReconfigureDvs_Task(config)
        changed, result = wait_for_task(task)
        return changed, result

    def destroy_private_vlan(self):
	config = vim.VMwareDVSConfigSpec()
        private_vlan_config = []
        pvlan = vim.dvs.VmwareDistributedVirtualSwitch.PvlanConfigSpec()
        pvlan.operation = vim.ConfigSpecOperation.remove
        pvlan.pvlanEntry = vim.dvs.VmwareDistributedVirtualSwitch.PvlanMapEntry()
        pvlan.pvlanEntry.primaryVlanId = self.public_vlan_id
        pvlan.pvlanEntry.pvlanType = vim.VmwareDistributedVirtualSwitchPvlanPortType.community
        pvlan.pvlanEntry.secondaryVlanId =  self.private_vlan_id
        private_vlan_config.append(pvlan)

        pvlan = vim.dvs.VmwareDistributedVirtualSwitch.PvlanConfigSpec()
        pvlan.operation = vim.ConfigSpecOperation.remove
        pvlan.pvlanEntry = vim.dvs.VmwareDistributedVirtualSwitch.PvlanMapEntry()
        pvlan.pvlanEntry.primaryVlanId = self.public_vlan_id
        pvlan.pvlanEntry.pvlanType = vim.VmwareDistributedVirtualSwitchPvlanPortType.promiscuous
        pvlan.pvlanEntry.secondaryVlanId = self.public_vlan_id
        private_vlan_config.append(pvlan)

        config.pvlanConfigSpec = private_vlan_config
        config.configVersion = self.dv_switch.config.configVersion
	try:
	        task = self.dv_switch.ReconfigureDvs_Task(config)
	        changed, result = wait_for_task(task)
	# couldn't get this exception to work. It rolls to the next one.
	except vim.fault.NotFound as not_found:
            self.module.fail_json(msg=str("Vlan Not Found! : ")+str(not_found))
        except Exception as e:
            self.module.fail_json(msg="Failure Deleting Vlans: {}".format(str(e.message)))
        return changed, result

    def state_destroy_private_vlan(self):
        changed = True
        result = None

        changed, result = self.destroy_private_vlan()
        self.module.exit_json(changed=changed, result=str(result))

    def state_exit_unchanged(self):
        self.module.exit_json(changed=False)

    def state_update_dvspg(self):
        self.module.exit_json(changed=False, msg="Currently not implemented.")

    def state_create_dvspg(self):
        changed = True
        result = None

        if not self.module.check_mode:
            changed, result = self.create_port_group()
        self.module.exit_json(changed=changed, result=str(result))

    def check_dvspg_state(self):
        self.dv_switch = find_dvs_by_name(self.content, self.switch_name)
	# Sorry a quick bypass. If we pass in a private_vland_id, and absent request, then return present to the init function to trick it to run destroy.
	# TODO lookup private vlan id.
	if self.state == 'absent':
	        if self.private_vlan_id > 0:
			return 'present'
        if self.dv_switch is None:
            raise Exception("A distributed virtual switch with name %s does not exist" % self.switch_name)
            return 'present'
        else:
            return 'absent'


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(dict(
                         switch_name=dict(required=True, type='str'),
                         public_vlan_id=dict(required=True, type='int'),
                         private_vlan_id=dict(required=True, type='int'),
                         allow_mac_changes=dict(required=False, type='bool',default=False),
                         allow_forged_transmits=dict(required=False, type='bool',default=False),
                         allow_promiscuous=dict(required=False, type='bool',default=False),
                         state=dict(default='present', choices=['present', 'absent'], type='str')))

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    if not HAS_PYVMOMI:
        module.fail_json(msg='pyvmomi is required for this module')

    vmware_dvs_portgroup = VMwareDvsPortgroup(module)
    vmware_dvs_portgroup.process_state()

from ansible.module_utils.vmware import *
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
