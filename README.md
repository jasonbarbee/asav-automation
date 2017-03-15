# Specific Use case in progress.

# Define inventory file like this
```
[all:vars]
Customer_VRF='example'
Customer_ID='12345678'
Subnet_SF_Inside='192.168.200.0'
Subnet_MGMT_Inside='192.168.201.0'
Subnet_Transport='192.168.202.0'
Vlan_SF_Inside='1101'
Vlan_MGMT_Inside='1102'
Vlan_Transport='1103'
```

Define a variable file like the all.vars included.
```yaml
---
    vlans:
      # This Vlan is the SourceFire Inside Vlan.
      - id: 2001
        name: Test_SFInside
      # This Vlan is the Management Network, and is leaked via VRF tables outside the customer's network. 
      - id: 2002
        name: Test_Mgmt
      # Customer's Transport Network
      - id: 2003
        name: Test_MPLS
    # This Template is the template we will add customer Vlans.
    vnic_template: 'test_template'
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


