#!/usr/bin/env python3

import sys
import getpass
import bloxone
import click
import threading
import concurrent.futures
import logging
from ibx_sdk.nios.exceptions import WapiRequestException
from ibx_sdk.nios.gift import Gift
from rich.console import Console

logger = logging.getLogger(__name__)
logging.basicConfig(filename="object_counter.log", level=logging.INFO)
console = Console()
wapi = Gift()


nios_uddi_types = {
    "record:a": "A",
    "record:aaaa": "AAAA",
    "record:alias": "ALIAS",
    "record:caa": "CAA",
    "record:cname": "CNAME",
    "record:dname": "DNAME",
    "record:dhcid": "DHCID",
    "record:ds": "DS",
    "record:https": "HTTPS",
    "record:mx": "MX",
    "record:naptr": "NAPTR",
    "record:ns": "NS",
    "record:srv": "SRV",
    "record:ptr": "PTR",
    "record:svcb": "SVCB",
    "record:txt": "TXT",
}


def connect_uddi(config):
    b1p = bloxone.b1platform(config)
    customer = b1p.get_current_tenant()
    b1 = bloxone.b1ddi(config)
    if customer:
        console.print(
            f"[bright_green]BloxOne[/] [white]Platform[/]: [bright white]{customer}[/bright white]"
        )
        console.print("[bright_green]Connected to BloxOne[/]")
        logger.info(f"Connected to UDDI Tenant: {customer}")
    return b1


def connect_nios(grid_mgr, username, wapi_ver):
    wapi.grid_mgr = grid_mgr
    wapi.wapi_ver = wapi_ver
    wapi.timeout = 1200
    password = getpass.getpass(f"Enter password for [{username}]: ")
    try:
        wapi.connect(username=username, password=password)
    except WapiRequestException as err:
        console.print(f"Error:[red] {err}[/red]")
        logger.error(f"Unable to connect to NIOS grid: {err}")
        sys.exit(1)
    else:
        print(f"Connected to Infoblox grid manager {wapi.grid_mgr}")
        logger.info(f"Connected to NIOS grid: {wapi.grid_mgr}")
    return wapi


def collect_nios_record(wapi, nios, b1, threads):
    nios_count = wapi.get(nios, params={"_max_results": 100000, "_return_as_object": 1})
    if nios_count.status_code != 200:
        logger.critical(f"NIOS Error: {nios_count.status_code} : {nios_count.text}")
    # Extract results array safely
    results = nios_count.json().get("result", [])
    print(f"Found {nios}: {len(results)}")
    for r in nios_count:
        check_existing = b1.get_id(
            "/dns/record",
            key="dns_absolute_name_spec",
            value=r["name"],
            include_path=False,
        )
        if check_existing:
            continue
        else:
            # TODO:add record
            delta_add = wapi.post()


@click.command()
@click.option(
    "-c",
    "--config",
    default="~/b1ddi/b1config.ini",
    show_default=True,
    required=True,
    help="BloxOne UDDI Config File",
)
@click.option("-g", "--grid-mgr", required=True, help="Infoblox Grid Manager")
@click.option(
    "-u",
    "--username",
    default="admin",
    show_default=True,
    help="Infoblox Admin Username",
)
@click.option(
    "-w",
    "--wapi-ver",
    default="2.13.7",
    show_default=True,
    help="Infoblox WAPI Version",
)
@click.option(
    "-m",
    "--threads",
    default=25,
    show_default=True,
    help="Number of threads to use for verification",
)
def main(config: str, grid_mgr: str, wapi_ver: str, username: str, threads: int):
    """Compare Record Object Counts between BloxOne DDI and NIOS\nVerify NIOS records in UDDI and display missing records"""
    b1 = connect_uddi(config)
    wapi = connect_nios(grid_mgr, username, wapi_ver)
    for record in nios_record_types:
        collect_nios_record(wapi, record, b1, threads)


if __name__ == "__main__":
    main()
