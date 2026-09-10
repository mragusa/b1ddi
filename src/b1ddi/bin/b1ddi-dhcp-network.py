#!/usr/bin/env python3

import bloxone
import click
from rich.console import Console
from rich.table import Column, Table
from rich import box


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
@click.option(
    "-g",
    "--get",
    is_flag=True,
    default=False,
    show_default=True,
    help="Retrieve DNS views",
)
def main(config: str, get: bool):
    total_networks = 0
    subnet_with_range = 0
    subnet_without_range = 0
    """Find UDDI Subnets with DHCP Ranges"""
    b1 = bloxone.b1ddi(config)
    uddi_networks = b1.get("/ipam/subnet", _limit=1000, _offset=0)
    if uddi_networks.status_code != 200:
        print(
            f"UDDI Error http error {uddi_networks.status_code} : {uddi_networks.text}"
        )
    else:
        for network in uddi_networks.json().get("results", []):
            total_networks += len(network)
            print(f"Checking: {network["address"]}")
            uddi_range = b1.get(
                "/ipam/range",
                _filter=f'parent=="{network["id"]}"',
            )
            if uddi_range.status_code != 200:
                print(
                    f"UDDI Error http error {uddi_range.status_code} : {uddi_range.text}"
                )
            else:
                if uddi_range.json().get("results") is not None:
                    for range in uddi_range.json().get("results"):
                        print(f"  Parent: {network['address']} contains dhcp range")
                        subnet_with_range += 1
                else:
                    print(f"  Parent: {network['address']} has no dhcp range")
                    subnet_without_range += 1

        print(f"Total Subnets: {total_networks}")
        print(f"Subnets with DHCP Ranges: {subnet_with_range}")
        print(f"Subnets without DHCP Ranges: {subnet_without_range}")


if __name__ == "__main__":
    main()
