# Automated Deployed of ASAv

# Automating the following tasks:
## Current Working Features
* Nexus creation of Vlans, SVIs, VRFs, Route leaking, HSRP
* UCS Vlans, Assignment to Port Channels, Assignment to VNIC Template
* Vmware Distributed switch - vlans, DVS port groups, Private Vlans and interfaces.

# Roadmap
* Automate SAv, SourceFire, and NGIPS OVA deployment.

Requirements
* python 2.7 or higher 
* Ansible 2.2.0 - issues updating, some NX bugs in 2.3.
* Custom modules included in the repo - in the library folder.
* Cisco UCSM-SDK - pip install ucsmsdk
* PyVmomi Vmware SDK - pip install pyvmomi

Tested on 
* UCS Version UCS 3.1.3
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

[NX:vars]
vnic_template_prefix='MOBL_vNIC_INT_'


[ucs]
10.2.2.2

[ucs:vars]
ucs_username="ucspe"
ucs_password="ucspe"

[vcenter]
10.1.1.1

[vcenter:vars]
vcenter_username="admin@vsphere.local"
vcenter_password="password"

```

Edit group variable files like customer.yml.
```yaml
---
    Customer_ID: '12345678'
    Customer_VRF: 'example'

    vlans:
      # This Vlan is the SourceFire Inside Vlan.
      - id: 2001
        name: SFInside
        subnet: '192.168.200.0'
      # This Vlan is the Management Network, and is leaked via VRF tables outside the customer's network.
      - id: 2002
        name: Mgmt
        subnet: '192.168.201.0'
      # Customer's Transport Network
      - id: 2003
        name: MPLS
        subnet: '192.168.202.0'

    private_vlans:
      SFInside:
        public: 36
        private: 37

    private_vlan_groups:
        - id: 36
          name: 'ASAInside'
        - id: 36

```

# Create Vlans on NX, UCS, VCenter
```
ansible-playbook -i inventory site.yml -t create
```
# Delete Vlans on All Systems NX, UCS, VCenter
```
ansible-playbook -i inventiry site.yml -t delete
```

#Run playbooks per system create/delete

```
ansible-playbook -i inventiry site.yml -t ucs-delete
ansible-playbook -i inventiry site.yml -t nx-delete
ansible-playbook -i inventiry site.yml -t vcenter-delete
```

```
ansible-playbook -i inventiry site.yml -t ucs-create
ansible-playbook -i inventiry site.yml -t nx-create
ansible-playbook -i inventiry site.yml -t vcenter-create
```

# Environment Setup
To use the UCS Library Module you need to add it to your PYTHONPATH

export PYTHONPATH="${PYTHONPATH}:/this/repos/library/folder

In my case, my .bashrc looks like this and everything is happy
```
export PYTHONPATH="/usr/lib/python2.6/site-packages"
export PYTHONPATH="${PYTHONPATH}:/home/myusername/ansible"
```

I had a strange issue with selinux on CentOS had to copy it into site packages manually from /usr/lib64/site-packages/selinux. CentOS issue.

References/Credits
https://github.com/btotharye/ansible-ucs
Look for some of these modules to head back to his repo when they are polished.

#ISSUES:
No issues known.