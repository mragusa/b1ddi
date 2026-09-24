#!/usr/bin/env python3

import bloxone
import click


def get_dhcp_host(b1, filter):
    if filter:
        dhcp_host = b1.get("/dhcp/host", _filter=f'name=="{filter}"')
    else:
        dhcp_host = b1.get("/dhcp/host")
    if dhcp_host.status_code != 200:
        print(dhcp_host.status_code, dhcp_host.text)
    else:
        return dhcp_host.json().get("results")


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
@click.option(
    "-f",
    "--filter",
    help="Retrieve DNS views",
)
def main(config: str, filter: str):
    """json dump dhcp host information"""
    b1 = bloxone.b1ddi(config)
    host = get_dhcp_host(b1, filter)
    if host:
        for h in host:
            print(host)


if __name__ == "__main__":
    main()
