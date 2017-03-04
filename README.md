# Specific Use case in progress.

# Define inventory file like this
[all:vars]
Customer_VRF='example'
Customer_ID='12345678'
Subnet_SF_Inside='192.168.200.0'
Subnet_MGMT_Inside='192.168.201.0'
Subnet_Transport='192.168.202.0'
Vlan_SF_Inside='1101'
Vlan_MGMT_Inside='1102'
Vlan_Transport='1103'

# Create Vlans on NX, UCS.
ansible-playbook site.yml -t create

# Delete Vlans on NX, UCS.
ansible-playbook site.yml -t create

