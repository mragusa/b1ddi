#!/usr/bin/env python3

import sys
import getpass
import bloxone
import click
from ibx_sdk.nios.exceptions import WapiRequestException
from ibx_sdk.nios.gift import Gift
from rich.console import Console
from rich.progress import Progress, TextColumn, SpinnerColumn

console = Console()
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
    "record:srv",
    "record:svcb",
    "record:txt",
]


def connect_uddi(config):
    b1p = bloxone.b1platform(config)
    customer = b1p.get_current_tenant()
    b1 = bloxone.b1ddi(config)
    if customer:
        console.print(f"Connected to Tenant: [white]{customer}[/white]")
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
        sys.exit(1)
    else:
        print(f"Connected to Infoblox grid manager {wapi.grid_mgr}")
    return wapi


def collect_uddi_record_count(b1, uddi):
    record_count = 0
    uddi_count = b1.get(
        "/dns/record", _filter=f"type=='{uddi}'", _limit=1000, _offset=0
    )
    if uddi_count.status_code != 200:
        print(f"UDDI Error http error {uddi_count.status_code} : {uddi_count.text}")
    else:
        for r in uddi_count.json().get("results", []):
            record_count += len(r)
    return record_count


def collect_nios_record_count(wapi, nios, b1, verify):
    nios_count = wapi.get(nios, params={"_max_results": 100000, "_return_as_object": 1})
    if nios_count.status_code != 200:
        print(f"NIOS Error: {nios_count.status_code} : {nios_count.text}")
    else:
        if verify:
            missing_records = []
            nios_in_uddi = 0
            with Progress(
                SpinnerColumn(),
                TextColumn("{task.completed}"),
                *Progress.get_default_columns(),
            ) as progress:
                count_task = progress.add_task(
                    "[white]UDDI Verificaton Progress",
                    total=len(nios_count.json().get("result")),
                )
                verified_task = progress.add_task("[green]Verified", total=None)
                missing_task = progress.add_task("[red]Missing", total=None)
                for r in nios_count.json().get("result"):
                    progress.update(count_task, advance=1)
                    if "ptrdname" in r:
                        verified = verify_nios_uddi(b1, r["ptrdname"])
                    else:
                        print(r["name"])
                        verified = verify_nios_uddi(b1, r["name"])
                    if verified == 1:
                        progress.update(verified_task, advance=1)
                    else:
                        if "ptrdname" in r:
                            missing_records.append(r["ptrdname"])
                        else:
                            missing_records.append(r["name"])
                        progress.update(missing_task, advance=1)
                    nios_in_uddi += verified
            print(f"Total {nios} verified: {nios_in_uddi}")
            print(
                f'UDDI Count: {nios_in_uddi} NIOS Count: {len(nios_count.json().get("result"))}'
            )
            with open("missing.txt", "a") as f:
                print(missing_records, file=f)
    return len(nios_count.json().get("result"))


def verify_nios_uddi(b1, hostname):
    record_verify = b1.get(
        "/dns/record", _filter=f"dns_absolute_name_spec=='{hostname}.'"
    )
    if record_verify.status_code != 200:
        print(f"{hostname}: {record_verify.status_code} : {record_verify.text}")
        return 0
    record = record_verify.json()
    results = record.get("results", [])
    if results:
        return 1
    return 0


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
    default="2.13.7",
    show_default=True,
    help="Infoblox WAPI version",
)
@click.option(
    "--verify",
    is_flag=True,
    default=False,
    help="Verify NIOS records exist in BloxOne DDI",
)
def main(config: str, grid_mgr: str, wapi_ver: str, username: str, verify: bool):
    """Compare Record Object Counts between BloxOne DDI and NIOS\nVerify NIOS records in UDDI and display missing records"""
    b1 = connect_uddi(config)
    wapi = connect_nios(grid_mgr, username, wapi_ver)
    for uddi, nios in zip(uddi_record_types, nios_record_types):
        uddi_count = collect_uddi_record_count(b1, uddi)
        nios_count = collect_nios_record_count(wapi, nios, b1, verify)
        print(f"{uddi} : BloxOne DDI Count: {uddi_count} NIOS Count: {nios_count}")


if __name__ == "__main__":
    main()
