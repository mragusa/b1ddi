#!/usr/bin/env python3

import bloxone
import click
from rich.table import Table
from rich.console import Console


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="Bloxone DDI Config File"
)
@click.option("-f", "--file", default="~/b1ddi/b1config.ini", help="CSV Input File")
@click.option(
    "-g", "--get", is_flag=True, help="Retrieve current subnet and service assignment"
)
@click.option(
    "-u", "--update", is_flag=True, help="Update current subnet and service assignment"
)
def main(config: str, get: bool):
    b1 = bloxone.b1ddi(config)
    if get:
        get_subnet(b1)


def get_subnet(b1):
    b1_subnet = b1.get("/ipam/subnet")
    if b1_subnet.status_code != 200:
        print(b1_subnet.status_code, b1_subnet.text)
    else:
        subnets = b1_subnet.json()
        subTable = Table(title="Current Subnet Assignment", row_styles=["dim", ""])
        subTable.add_column("Address", justify="center", style="green")
        subTable.add_column("Service Instance", justify="center", style="bright_white")
        for net in subnets["results"]:
            subTable.add_row(net["address"], net["dhcp_host"])
        console = Console()
        console.print(subTable)


if __name__ == "__main__":
    main()
