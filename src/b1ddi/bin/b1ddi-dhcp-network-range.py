#!/usr/bin/env python3
# TODO define better functions

import bloxone
import click
from rich.console import Console

console = Console()


def get_uddi_subnets(b1):
    # Poll UDDI with limits and offsets to get all networks
    uddi_networks = b1.get("/ipam/subnet", _limit=1000, _offset=0)
    if uddi_networks.status_code != 200:
        print(
            f"UDDI Error http error {uddi_networks.status_code} : {uddi_networks.text}"
        )
    else:
        return uddi_networks.json().get("results", [])


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
    subnet_with_range = []
    subnet_with_range_count = 0
    """Find UDDI Subnets with DHCP Ranges"""
    b1 = bloxone.b1ddi(config)
    uddi_subnets = get_uddi_subnets(b1)
    if uddi_subnets:
        for network in uddi_subnets:
            total_networks += len(network)
            console.print(
                f"[green]Checking: {network["address"]}/{network["cidr"]} [/green]"
            )
            # Search dhcp range based on network id
            uddi_range = b1.get(
                "/ipam/range",
                _filter=f'parent=="{network["id"]}"',
            )
            if uddi_range.status_code != 200:
                print(
                    f"UDDI Error http error {uddi_range.status_code} : {uddi_range.text}"
                )
            else:
                if uddi_range.json().get("results"):
                    for range in uddi_range.json().get("results"):
                        print(
                            f"UDDI Subnet: {network['address']}/{network['cidr']} has DHCP Range: {range['start']} - {range['end']}"
                        )
                        subnet_with_range.append(
                            f'{network["address"]}/{network["cidr"]}'
                        )
                    subnet_with_range_count += 1

        print(f"Total Subnets: {total_networks}")
        print(f"Subnets with DHCP Ranges: {subnet_with_range_count}")
        for s in subnet_with_range:
            print(s)
    else:
        print("No subnets found in UDDI")


if __name__ == "__main__":
    main()
