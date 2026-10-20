#!/usr/bin/env python3

import sys
import time
import getpass
import bloxone
import click
import threading
import concurrent.futures
import logging
from ibx_sdk.nios.exceptions import WapiRequestException
from ibx_sdk.nios.gift import Gift
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TextColumn, SpinnerColumn

console = Console()
logger = logging.getLogger(__name__)
logging.basicConfig(filename="object_counter.log", level=logging.INFO)
tableRecords = Table("UDDI", "NIOS", "Type", "Missing", title="UDDI/NIOS Object Count")
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


def collect_uddi_record_count(b1, uddi):
    record_count = 0
    offset = 0

    while True:
        # Retry the same page if rate-limited.
        for attempt in range(5):
            response = b1.get(
                "/dns/record",
                _filter=f'type=="{uddi}"',
                _fields="id",
                _limit=1000,
                _offset=offset,
            )

            # Handle rate limiting.
            if response.status_code == 429:
                if attempt == 4:
                    raise RuntimeError(
                        f"UDDI rate limit exceeded after "
                        f"5 attempts: {response.text}"
                    )
                    logger.critical(f"{uddi} rate limit exceeded: {response.text}")

                logger.critical(f"{uddi} rate limited: {response.text}")
                retry_after = response.headers.get("Retry-After")

                if retry_after and retry_after.isdigit():
                    delay = int(retry_after)
                else:
                    delay = min(2**attempt, 30)

                print(
                    f"{uddi}: Rate limited. " f"Retrying in {delay}s",
                    flush=True,
                )

                time.sleep(delay)
                continue

            # Handle other HTTP errors.
            if response.status_code != 200:
                raise RuntimeError(
                    f"UDDI HTTP {response.status_code}: " f"{response.text}"
                )

            # Parse response.
            data = response.json()

            if not isinstance(data, dict) or not isinstance(data.get("results"), list):
                raise ValueError(f"Unexpected UDDI response: {data}")

            results = data["results"]

            # Successfully retrieved this page.
            break

        else:
            raise RuntimeError("UDDI retries exhausted")

        # Count the records returned on this page.
        page_count = len(results)
        record_count += page_count

        # Exit the OUTER while loop when no records remain.
        if page_count == 0:
            break

        # Advance to the next page.
        offset += page_count

        # Reduce request frequency.
        time.sleep(0.5)

    return record_count


def collect_nios_record_count(wapi, nios, b1, verify, threads):
    nios_count = wapi.get(nios, params={"_max_results": 100000, "_return_as_object": 1})
    if nios_count.status_code != 200:
        logger.critical(f"NIOS Error: {nios_count.status_code} : {nios_count.text}")
        return 0

    # Extract results array safely
    results = nios_count.json().get("result", [])

    if verify and results:
        uddi_verify_process(b1, nios, results, threads)

    return len(results)


def verify_nios_uddi(b1, hostname, type):
    """Performs the network lookups. Keeps file and list manipulation out of here."""
    try:
        if type == "record:ptr":
            record_verify = b1.get(
                "/dns/record",
                _filter=f"dns_rdata=='{hostname}.' and type=='PTR'",
            )
        else:
            record_verify = b1.get(
                "/dns/record", _filter=f"dns_absolute_name_spec=='{hostname}.'"
            )
        if record_verify.status_code != 200:
            logger.critical(
                f"{hostname} verification: {record_verify.status_code} : {record_verify.text}"
            )
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
        logger.critical(f"Error verifying {hostname}: {e}")
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
            f"[white]UDDI {nios} Verification Progress", total=total_records
        )
        verified_task = progress.add_task("[green]Verified", total=None)
        missing_task = progress.add_task("[red]Missing", total=None)

        def worker(r):
            nonlocal nios_in_uddi

            # Determine correct lookup string
            target_name = r["ptrdname"] if "ptrdname" in r else r["name"]

            # 1. Thread-safe execution of network tasks (runs fully parallelized)
            is_verified, metadata_lines = verify_nios_uddi(b1, target_name, nios)

            # 2. Safely synchronize list appending and UI stats
            with ui_and_data_lock:
                progress.update(count_task, advance=1)

                if is_verified:
                    nios_in_uddi += 1
                    verified_records_buffer.extend(metadata_lines)
                    progress.update(verified_task, advance=1)
                else:
                    if "ptrdname" in r:
                        missing_records.append(f"{r["ptrdname"]}, {nios}")
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
    if missing_records:
        tableRecords.add_row(
            str(nios_in_uddi), str(total_records), nios, str("\n".join(missing_records))
        )
    else:
        tableRecords.add_row(str(nios_in_uddi), str(total_records), nios, "None")


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
    totalTable = Table("Type", "UDDI", "NIOS", title="Total Object Count")
    for uddi, nios in zip(uddi_record_types, nios_record_types):
        uddi_count = collect_uddi_record_count(b1, uddi)
        nios_count = collect_nios_record_count(wapi, nios, b1, verify, threads)
        totalTable.add_row(nios, str(uddi_count), str(nios_count))
    console.print(totalTable)
    console.print(tableRecords)


if __name__ == "__main__":
    main()
