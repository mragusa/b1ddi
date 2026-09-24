#!/usr/bin/env python3

import bloxone
import click


def get_subnet(b1, filter):
    if filter:
        dhcp_subnet = b1.get("/ipam/subnet", _filter=f'address=="{filter}"')
    else:
        dhcp_subnet = b1.get("/ipam/subnet")
    if dhcp_subnet.status_code != 200:
        print(dhcp_subnet.status_code, dhcp_subnet.text)
    else:
        return dhcp_subnet.json().get("results")


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
@click.option(
    "-f",
    "--filter",
    default="10.0.0.0",
    show_default=True,
    help="Filter subnet output",
)
def main(config: str, filter: str):
    """Infoblox UDDI Network Script"""
    b1 = bloxone.b1ddi(config)
    subnet = get_subnet(b1, filter)
    if subnet:
        for s in subnet:
            print(s)
    else:
        print("Subnet not found")


if __name__ == "__main__":
    main()
