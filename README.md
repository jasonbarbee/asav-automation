# Automated Deployed of ASAv.

# Automating the following tasks:
## Features that are Working:
* Nexus creation of Vlans, SVIs, VRFs, Route leaking, HSRP
* UCS Vlans, Assignment to Port Channels, Assignment to VNIC Template
* Vmware Distributed switch - vlans, DVS port groups, Private Vlans and interfaces.
# Next Up:
* ASAv, SourceFire, and NGIPS OVA deployment.

Requirements
* python 2.7 or higher 
* Ansible 2.2+
* Custom modules included in the repo
* Cisco UCSM-SDK - pip install ucsmsdk
* PyVmomi Vmware SDK - pip install pyvmomi

Tested on 
* UCS Version 2.2(6d)
* Ansible 2.2.2
* VCenter 6.0.0

# Define Ansible Inventory file like this
```yaml
[NX]
192.168.123.10 SVI_oct='2'
192.168.123.11 SVI_oct='3'

[NX:vars]
username='nxapi'
password='nxapi'

[ucs]
192.168.123.206

[ucs:vars]
ucs_username="ucspe"
ucs_password="ucspe"

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

In my case, it was
 
export PYTHONPATH="/usr/lib/python2.6/site-packages"
export PYTHONPATH="${PYTHONPATH}:/home/mfuser/ansible"

I had a strange issue with selinux on CentOS had to copy it into site packages manually from /usr/lib64/site-packages/selinux

References/Credits
https://github.com/btotharye/ansible-ucs
Look for some of these modules to head back to his repo when they are polished.

TODO:
Fix naming on NX - prefixing vlans.

