#!/usr/bin/env python3

import bloxone
import csv
import click
from rich.table import Table
from rich.console import Console


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="Bloxone DDI Config File"
)
@click.option(
    "-g", "--get", is_flag=True, help="Retrieve current subnet and service assignment"
)
@click.option(
    "-u",
    "--update",
    is_flag=True,
    help="Update subnet and service assignment from CSV import file",
)
@click.option("-f", "--file", default="~/import.csv", help="CSV Input File")
def main(config: str, get: bool, file: str, update: bool):
    """This tool will retreive all current subnets assisgned to a UDDI tenant and display network and service instance ID
    If a CSV input file is used, all subnets and their corresponding dhcp ranges will be updated to the provided HA group
    """

    b1 = bloxone.b1ddi(config)
    if get:
        get_subnet(b1)
    if update:
        process_file(b1, file)


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


def get_range(b1):
    # TODO
    # Update this method to find ranges based on subnets and return for the subnet table
    dhcp_range = b1.get("/ipam/range")
    if dhcp_range.status_code != 200:
        print(dhcp_range.status_code, dhcp_range.text)
    else:
        ranges = dhcp_range.json()
        for x in ranges["results"]:
            print(x["parent"])


def process_file(b1, file):
    subnet_ha_groups = {}
    if file:
        with open(file, newline="\n") as csvfile:
            network_csv_file = csv.reader(csvfile, delimiter=",", quotechar='"')
            for net in network_csv_file:
                # Find subnet ID of provided network
                sub_id = get_subnet_id(b1, net[0])
                # Find dhcp ranges based on parent key and search with subnet id
                ran_id = get_range_id(b1, sub_id)
                # Populate dictionary with ha id to reduce lookups against cloud api
                if net[1] not in subnet_ha_groups:
                    ha_id = get_ha_id(b1, net[1])
                    subnet_ha_groups[net[1]] = ha_id
                print(
                    "Network: {} Subnet ID: {} HA Group: {} HA ID: {}".format(
                        net[0], sub_id, net[1], subnet_ha_groups[net[1]]
                    )
                )
                if ran_id:
                    print("Range: {}".format(ran_id))
                # updated_subnet(b1, sub_id, subnet_ha_groups[net[1]])
    else:
        print("CSV Input File Missing")


def get_ha_id(b1, ha_group):
    ha_id = b1.get_id("/dhcp/ha_group", key="name", value=ha_group)
    return ha_id


def get_subnet_id(b1, address):
    sub_id = b1.get_id("/ipam/subnet", key="address", value=address)
    return sub_id


def get_range_id(b1, parent):
    range_id = b1.get_id("/ipam/range", key="parent", value=parent)
    return range_id


def update_subnet(b1, subnet_id, ha_group_id):
    print("Updating {}".format(subnet_id))
    updateBody = {"dhcp_host": ha_group_id}
    updated_subnet = b1.replace("/ipam/subnet", id=subnet_id, body=updateBody)
    if updated_subnet.status_code != 200:
        print(updated_subnet.status_code, updated_subnet.text)
    else:
        print("Subnet Updated: {} {}".format(subnet_id, ha_group_id))


def update_range(b1, range_id, ha_group_id):
    print("Updating {}".format(subnet_id))
    updateBody = {"dhcp_host": ha_group_id}
    updated_range = b1.replace("/ipam/subnet", id=subnet_id, body=updateBody)
    if updated_range.status_code != 200:
        print(updated_range.status_code, updated_range.text)
    else:
        print("Subnet Updated: {} {}".format(subnet_id, ha_group_id))


if __name__ == "__main__":
    main()
