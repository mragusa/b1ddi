#!/usr/bin/env python3

import bloxone
import click
import csv


def get_range(b1, range_start):
    b1_dhcp_range = b1.get("/ipam/range", _filter=f'start=="{range_start}"')
    if b1_dhcp_range.status_code != 200:
        print(b1_dhcp_range.status_code, b1_dhcp_range.text)
    else:
        return b1_dhcp_range.json().get("results")


def get_subnet_address(b1, subnet_id):
    subnet_address = b1.get("/ipam/subnet", id=subnet_id)
    if subnet_address.status_code != 200:
        print(subnet_address.status_code, subnet_address.text)
    else:
        return subnet_address.json().get("result").get("address")


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
@click.option("-f", "--file", help="DHCP Range Input File")
def main(config: str, file: str):
    """Find UDDI Subnets from DHCP Range Start Octets
    Input file:
    header, DHCP Member, start, end
    range, Test, 10.0.0.10, 10.0.0.100
    Print output can be used by b1ddi-dhcp-network-service-instance.py to change member assignment
    """
    b1 = bloxone.b1ddi(config)
    if file:
        with open(file, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                dhcp_range = get_range(b1, row["Start"])
                if dhcp_range:
                    for r in dhcp_range:
                        id = r["parent"].split("/")
                        subnet_address = get_subnet_address(b1, id[2])
                        if subnet_address:
                            print(f'{subnet_address}, "{row["DHCP Member"]}"')


if __name__ == "__main__":
    main()
