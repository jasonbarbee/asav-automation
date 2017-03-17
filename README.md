# Specific Use case in progress. Breaking Changes coming.
# Automating the following tasks:
* Nexus creation of Vlans, SVIs, VRFs, Route leaking, HSRP
* UCS Vlans, Assignment to Port Channels, Assignment to VNIC Template
* Vmware Distributed switch

# Define inventory file like this
```
[all:vars]
Customer_VRF='example'
Customer_ID='12345678'
Subnet_SF_Inside='192.168.200.0'
Subnet_MGMT_Inside='192.168.201.0'
Subnet_Transport='192.168.202.0'

```

Edit group variable files like the group_vars/all.yml.
```yaml
---
    Customer_ID: '12345678'
    Customer_VRF: 'example'

    vlans:
      # This Vlan is the SourceFire Inside Vlan.
      - id: 2001
        name: Test_SFInside
        subnet: '192.168.200.0'
      # This Vlan is the Management Network, and is leaked via VRF tables outside the customer's network. 
      - id: 2002
        name: Test_Mgmt
        subnet: '192.168.201.0'
      # Customer's Transport Network
      - id: 2003
        name: Test_MPLS
        subnet: '192.168.202.0'
```
Confirm the UCS VNIC Templates - roles/ucs/vars/vnics.yml
```yaml
    # Site Specific UCS Customer VNICs
    vnic_template_a: 'MOBL_vNIC_INT_A'
    vnic_template_b: 'MOBL_vNIC_INT_B'
```

# Create Vlans on NX, UCS.
ansible-playbook site.yml -t create

# Delete Vlans on NX, UCS.
ansible-playbook site.yml -t delete

# Environment Setup
To use the UCS Library Module you need to add it to your PYTHONPATH

export PYTHONPATH="${PYTHONPATH}:/this/repos/library/folder

References/Credits
https://github.com/btotharye/ansible-ucs
Look for some of these modules to head back to his repo when they are polished.


