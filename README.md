# Overview
Collection of scripts for interfacing with Infoblox UDDI platform

## Installation
The following python packages will be required to run these tools:
- [bloxone](https://github.com/ccmarris/python-bloxone)
- [click](https://click.palletsprojects.com/en/stable/)
- [click-option-group](https://click-option-group.readthedocs.io/en/latest/)
- [prettytable](https://github.com/prettytable/prettytable)
- [rich](https://github.com/Textualize/rich)
```
pip3 install -r requirements.txt
```

## Scripts
| B1TDC Tools | Description |
| ---- | ---- |
| b1td-named-list.py | Add, Update, Delete B1TDC Named Lists |
| b1tdc.py | Get B1TDC Objects and display them on screen |

| B1DDI Tools | Description |
| ---- | ---- |
| b1ddi-framework.py | Basic B1DDI Script |
| b1ztp-join-token.py | Get, Add, Delete B1DDI Join Tokens |
| b1infra-host-services.py | Get, Add, Update Host / Service Assignment and Start / Stop Services |
| b1ddi-dns-nsg.py | Get, Add, Delete B1DDI Auth NSG |
| b1ddi-dns-profile.py | Get, Add, Delete B1DDI Global DNS Profiles |
| b1ddi-dns-view.py | Get, Add, Delete B1DDI Auth NSG |
| b1ddi-dhcp-ha.py | Get, Add, Delete B1DDI DHCP HA Groups |
| b1ddi-dhcp-ipspace.py | Get, Add, Delete B1DDI IP Space |
| b1ddi-dhcp-profile.py | Get, Add, Delete B1DDI Global DHCP Profiles |
| b1ddi-dhcp-options.py | Get, Add DHCP Options |
| b1ddi-dhcp-option-filters.py | Get, Add DHCP Options Filters |
| b1ddi-dhcp-network-service-instance.py | Get,Update Subnet/Range Service Assignment |

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
