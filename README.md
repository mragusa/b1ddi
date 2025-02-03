# Overview
Collection of scripts for interfacing with Infoblox B1DDI platform

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


## UDDI Process
1. Create Join Tokens for BloxOne hardware or virtual machine
    - b1ztp-join-token.py example
2. Update Joined Host Display Names
    - b1infra-host-services.py
3. Create IP Space
    - b1ddi-dhcp-ipspace.py
4. Create DHCP Global Config
    - b1ddi-dhcp-profile.py
5. Crete DNS Global Config
    - b1ddi-dns-profile.py
6. Crete DHCP High Availablity Groups
    - b1ddi-dhcp-ha.py
7. Create Name Server Groups
    - b1ddi-dns-nsg.py
8. Create DNS View
    - b1ddi-dns-view.py
9. Import DHCP Options
    - b1ddi-dhcp-options.py	
10. Import DHCP Option Filters

## Usage
```
b1td-named-lists.py --help
Usage: b1td-named-lists.py [OPTIONS]

Options:
  Required Options:
    --config TEXT                 B1DDI Configuration INI file
  Batch Operations:
    -f, --file TEXT               CSV file containing data for processing
  B1TD NamedList Actions:
    -l, --listnl                  Use this method to retrieve information on
                                  all Named List objects for the account. Note
                                  that list items are not returned for this
                                  operation
    -c, --create                  Use this method to create a Named List
                                  object.
    -d, --delete                  Use this method to delete Named List
                                  objects. Deletion of multiple lists is an
                                  all-or-nothing operation (if any of the
                                  specified lists can not be deleted then none
                                  of the specified lists will be deleted).
    -p, --patch                   Use this method to insert items for
                                  multiple Named List objects. Note that
                                  duplicated items correspondig to named list
                                  are silently skipped and only new items are
                                  appended to the named list. Note that DNSM,
                                  TI, Fast Flux and DGA lists cannot be
                                  updated. Only named lists of Custom List
                                  type can be updated by this operation. If
                                  one or more of the list ids is invalid, or
                                  the list is of invalid type then the entire
                                  operation will be failed.  The Custom List
                                  Items represent the list of the FQDN or IPv4
                                  addresses to define whitelists and
                                  blacklists for additional protection.
  B1TD NamedList Fields:
    -n, --name TEXT               The identifier for a Named List object.
    -i, --item TEXT               Add the item in the custom list using this
                                  field.
    --comment TEXT                Add the description/comments to each item in
                                  the custom list using this field.
    --confidence [LOW|MEDIUM|HIGH]
                                  Confidence level of item
  --help                          Show this message and exit.
```

### Example
#### Create New List
```
b1td-named-lists.py -c -n ChickenDinner -i "www.google.com" --comment "This is google"
```
#### Update Existing List
```
b1td-named-lists.py -p -n ChickenDinner -i www.yahoo.com --comment yahoo
```
#### Delete Item From Existing List
```
b1td-named-lists.py -d -n ChickenDinner -i www.yahoo.com --comment yahoo
```
#### Delete List
```
b1td-named-lists.py -d -n ChickenDinner
```
#### Batch Process From File
```
b1td-named-lists.py -f file_test_nl.csv
```

#### Sample Batch Processing File Format
##### Create New Lists
```
create,ChickenDinner,Google,www.google.com
```
##### Update Existing Lists
```
update,ChickenDinner,Yahoo,www.yahoo.com
update,ChickenDinner,Bing,www.bing.com
```
##### Delete Item from List
```
deleteitem,ChickenDinner,Yahoo,www.yahoo.com
deleteitem,ChickenDinner,Google,www.google.com
```
##### Delete List
```
delete,ChickenDinner
```


[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
