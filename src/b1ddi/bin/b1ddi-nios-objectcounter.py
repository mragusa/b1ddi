#!/usr/bin/env python3

import sys
import getpass
import bloxone
import click
from ibx_sdk.nios.exceptions import WapiRequestException
from ibx_sdk.nios.gift import Gift

wapi = Gift()
uddi_record_types = [
    "A",
    "AAAA",
    "ALIAS",
    "CAA",
    "CNAME",
    "DNAME",
    "DHCID",
    "DS",
    "HTTPS",
    "MX",
    "NAPTR",
    "NS",
    "PTR",
    "SOA",
    "SSHFP",
    "SRV",
    "SVCB",
    "TXT",
]

nios_record_types = [
    "record:a",
    "record:aaaa",
    "record:alias",
    "record:caa",
    "record:cname",
    "record:dname",
    "record:dhcid",
    "record:ds",
    "record:https",
    "record:mx",
    "record:naptr",
    "record:ns",
    "record:ptr",
    "record:soa",
    "record:sshfp",
    "record:srv",
    "record:svcb",
    "record:txt",
]


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="BloxOne UDDI Config File"
)
@click.option(
    "-u",
    "--username",
    default="admin",
    show_default=True,
    help="Infoblox admin username",
)
@click.option("-g", "--grid-mgr", required=True, help="Infoblox Grid Manager")
@click.option(
    "-w",
    "--wapi-ver",
    default="2.12.3",
    show_default=True,
    help="Infoblox WAPI version",
)
def main(config: str, grid_mgr: str, wapi_ver: str, username: str):
    """Compare Object Counts between BloxOne DDI and NIOS"""
    b1 = bloxone.b1ddi(config)
    wapi.grid_mgr = grid_mgr
    wapi.wapi_ver = wapi_ver
    wapi.timeout = 600
    password = getpass.getpass(f"Enter password for [{username}]: ")
    try:
        wapi.connect(username=username, password=password)
    except WapiRequestException as err:
        print(f"Error: {err}")
        sys.exit(1)
    else:
        print(f"Connected to Infoblox grid manager {wapi.grid_mgr}")
    for uddi, nios in zip(uddi_record_types, nios_record_types):
        uddi_count = b1.get("/dns/record", type=uddi)
        nios_count = wapi.get(
            nios, params={"_max_results": 100000, "_return_as_object": 1}
        )
        print(
            f"{uddi} / {nios}: BloxOne DDI Count: {uddi_count.json().get("results")}, NIOS Count: {nios_count["result"]}"
        )


if __name__ == "__main__":
    main()
