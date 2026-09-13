#!/usr/bin/env python3

import sys
import getpass
import bloxone
import click
import threading
import concurrent.futures
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
    "SRV",
    "PTR",
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
    "record:srv",
    "record:ptr",
    "record:svcb",
    "record:txt",
]


def connect_uddi(config):
    b1p = bloxone.b1platform(config)
    customer = b1p.get_current_tenant()
    b1 = bloxone.b1ddi(config)
    if customer:
        console.print(
            f"[bright_green]BloxOne[/] [white]Platform[/]: [bright white]{customer}[/bright white]"
        )
        console.print("[bright_green]Connected to BloxOne[/]")
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


def collect_nios_record_count(wapi, nios, b1, verify, threads):
    nios_count = wapi.get(nios, params={"_max_results": 100000, "_return_as_object": 1})
    if nios_count.status_code != 200:
        print(f"NIOS Error: {nios_count.status_code} : {nios_count.text}")
        return 0

    # Extract results array safely
    results = nios_count.json().get("result", [])

    if verify and results:
        uddi_verify_process(b1, nios, results, threads)

    return len(results)


def verify_nios_uddi(b1, hostname):
    """Performs the network lookups. Keeps file and list manipulation out of here."""
    try:
        record_verify = b1.get(
            "/dns/record", _filter=f"dns_absolute_name_spec=='{hostname}.'"
        )
        if record_verify.status_code != 200:
            print(f"{hostname}: {record_verify.status_code} : {record_verify.text}")
            return False, []

        results = record_verify.json().get("results", [])
        if results:
            # Pass matched record metadata back up to be safely saved under thread lock
            records_metadata = [
                f"{hostname}, {r['id']}, {r['created_at']}" for r in results
            ]
            return True, records_metadata

        return False, []
    except Exception as e:
        print(f"Error verifying {hostname}: {e}")
        return False, []


def uddi_verify_process(b1, nios, results_list, threads):
    missing_records = []
    verified_records_buffer = []
    nios_in_uddi = 0
    total_records = len(results_list)

    # Thread locks to secure concurrent updates
    ui_and_data_lock = threading.Lock()

    with Progress(
        SpinnerColumn(),
        TextColumn("{task.completed}"),
        *Progress.get_default_columns(),
    ) as progress:

        count_task = progress.add_task(
            "[white]UDDI Verification Progress", total=total_records
        )
        verified_task = progress.add_task("[green]Verified", total=None)
        missing_task = progress.add_task("[red]Missing", total=None)

        def worker(r):
            nonlocal nios_in_uddi

            # Determine correct lookup string
            target_name = r["ptrdname"] if "ptrdname" in r else r["name"]

            # 1. Thread-safe execution of network tasks (runs fully parallelized)
            is_verified, metadata_lines = verify_nios_uddi(b1, target_name)

            # 2. Safely synchronize list appending and UI stats
            with ui_and_data_lock:
                progress.update(count_task, advance=1)

                if is_verified:
                    nios_in_uddi += 1
                    verified_records_buffer.extend(metadata_lines)
                    progress.update(verified_task, advance=1)
                else:
                    if "ptrdname" in r:
                        missing_records.append(r["ptrdname"])
                    else:
                        missing_records.append(f'{r["name"]}, {nios}')
                    progress.update(missing_task, advance=1)

        # 3. Handle processing with 50 background workers max
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker, r) for r in results_list]
            concurrent.futures.wait(futures)

    # 4. Safe Batch File Operations (Happens once outside loops)
    if verified_records_buffer:
        with open("verified_records.txt", "a") as f:
            f.write("\n".join(verified_records_buffer) + "\n")

    if missing_records:
        with open("missing_records.txt", "a") as f:
            f.write("\n".join(missing_records) + "\n")

    # Summary Output
    print(f"Total {nios} verified: {total_records}")
    print(f"UDDI Count: {nios_in_uddi} NIOS Count: {total_records}")
    if missing_records:
        print(f"Missing {nios} records: {len(missing_records)}")
        print("Review missing_records.txt file")


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
    "--verify",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verify NIOS records exist in BloxOne DDI",
)
@click.option(
    "-m",
    "--threads",
    default=25,
    show_default=True,
    help="Number of threads to use for verification",
)
def main(
    config: str, grid_mgr: str, wapi_ver: str, username: str, verify: bool, threads: int
):
    """Compare Record Object Counts between BloxOne DDI and NIOS\nVerify NIOS records in UDDI and display missing records"""
    b1 = connect_uddi(config)
    wapi = connect_nios(grid_mgr, username, wapi_ver)
    for uddi, nios in zip(uddi_record_types, nios_record_types):
        uddi_count = collect_uddi_record_count(b1, uddi)
        nios_count = collect_nios_record_count(wapi, nios, b1, verify, threads)
        print(f"{uddi} : BloxOne DDI Count: {uddi_count} NIOS Count: {nios_count}")


if __name__ == "__main__":
    main()
