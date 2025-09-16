#!/usr/bin/env python3

import bloxone
import click
from rich.console import Console
from rich.table import Table


@click.command()
@click.option(
    "-c",
    "--config",
    default="~/b1ddi/b1config.ini",
    show_default=True,
    help="bloxone ddi config file",
)
@click.option(
    "-g",
    "--get",
    is_flag=True,
    default=False,
    show_default=True,
    help="Retrieve Auth Zones from UDDI",
)
@click.option(
    "-c",
    "--create",
    is_flag=True,
    default=False,
    show_default=True,
    help="Create UDDI Auth Zone",
)
def main(config: str, get: bool, create: bool):
    b1 = bloxone.b1ddi(config)
    if get:
        get_authzone(b1)
    if create:
        create_authzone(b1)


def get_authzone(b1):
    b1_authzone = b1.get("/dns/auth_zone")
    if b1_authzone.status_code != 200:
        print(b1_authzone.status_code, b1_authzone.text)
    else:
        auth_zones = b1_authzone.json()
        print_zones(b1, auth_zones)


def print_zones(b1, auth_zones):
    table = Table(title="Infoblox UDDI Auth Zones")
    table.add_column("FQDN", justify="center")
    table.add_column("ID", justify="center")
    table.add_column("NSG", justify="center")
    table.add_column("Grid Primaries", justify="center")
    table.add_column("Grid Secondaries", justify="center")
    table.add_column("Primary Type", justify="center")
    for az in auth_zones["results"]:
        table.add_row(
            az["fqdn"],
            az["id"],
            get_nsgs_name(b1, az["nsgs"][0]),
            str(az["grid_primaries"]),
            str(az["grid_secondaries"]),
            str(az["primary_type"]),
        )
    console = Console()
    console.print(table)


def get_nsgs_name(b1, nsgs):
    b1_nsg_id = nsgs.split("/")
    b1_nsgs = b1.get("/dns/auth_nsg", id=b1_nsg_id[2])
    if b1_nsgs.status_code != 200:
        print(f"Error retreiving nsgs: {b1_nsgs.status_code} {b1_nsgs.text}")
    else:
        nsgs = b1_nsgs.json()
        return nsgs["result"]["name"]


if __name__ == "__main__":
    main()
