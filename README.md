# Overview
Collection of scripts for interfacing with Infoblox B1DDI platform

## Installation
The following python packages will be required to run these tools:
- [bloxone](https://github.com/ccmarris/python-bloxone)
- [click](https://click.palletsprojects.com/en/stable/)
- [click-option-group](https://click-option-group.readthedocs.io/en/latest/)
- [prettytable](https://github.com/prettytable/prettytable)

```
pip3 install requirements.txt
```

## Scripts
| Name | Description |
| ---- | ---- |
| b1td-named-list.py | Add, Update, Delete B1TDC Named Lists |

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
