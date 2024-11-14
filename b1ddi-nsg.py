#!/usr/bin/env python3


import bloxone
import json
from prettytable import PrettyTable
import click

# TODO
# Add functionality for external primaries, external secondaries,  additional options for niosx hosts
# Add functionality for providing tsig keys


@click.command()
@click.option(
    "-c", "--config", default="b1config.ini", help="BloxOne Configuration File"
)
@click.option(
    "-g",
    "--get",
    is_flag=True,
    default=False,
    help="Retreive BloxOne Hosts and AuthNSG",
)
@click.option("-n", "--new", is_flag=True, default=False, help="Create BloxOne AuthNSG")
@click.option(
    "-d", "--delete", is_flag=True, default=False, help="Delete BloxOne AuthNSG"
)
@click.option("--host", multiple=True, default=[], help="BloxOne Host")
@click.option("--ansgname", help="NSG Name")
@click.option("--comment", help="NSG Comment")
@click.option("--ansgid", help="Auth NSG ID")
def main(config, get, new, delete, host, ansgname, comment, ansgid):
    b1ddi = bloxone.b1ddi(config)
    if get:
        # Display available hosts
        get_dns_hosts(b1ddi)
        # Display current nsg
        get_auth_nsg(b1ddi)
    # Create NSG
    if new:
        create_auth_nsg(b1ddi, host, ansgname, comment)
    if delete:
        delete_auth_nsg(b1ddi, ansgid)


def get_dns_hosts(b1ddi):
    table = PrettyTable()
    response = b1ddi.get("/dns/host")
    if response.status_code == 200:
        # print(response.json())
        table.field_names = [
            "Address",
            "Name",
            "ID",
            "Comment",
            "Version",
            "Serial Number",
            "Type",
        ]
        dnsHosts = response.json()
        for x in dnsHosts["results"]:
            # print(x["address"])
            table.add_row(
                [
                    x["address"],
                    x["name"],
                    x["id"],
                    x["comment"],
                    x["current_version"],
                    x["tags"]["host/serial_number"],
                    x["type"],
                ]
            )
        print(table)
    else:
        print(response.status_code, response.text)


def get_auth_nsg(b1ddi):
    table = PrettyTable()
    response = b1ddi.get("/dns/auth_nsg")
    if response.status_code == 200:
        authNsg = response.json()
        table.field_names = [
            "Name",
            "Comment",
            "ID",
            "External Primaries",
            "NIOS-X Host",
            "NSG",
            "Tags",
        ]
        for x in authNsg["results"]:
            table.add_row(
                [
                    x["name"],
                    x["comment"],
                    x["id"],
                    x["external_primaries"],
                    x["internal_secondaries"],
                    x["nsgs"],
                    x["tags"],
                ]
            )
        print(table)
    else:
        print(response.status_code, response.text)


def create_auth_nsg(b1ddi, host, ansgname, comment):
    niosx_hosts = []
    for nxh in host:
        niosx_hosts.append({"host": nxh})
    ansgBody = {
        "comment": comment,
        "internal_secondaries": niosx_hosts,
        "name": ansgname,
    }
    response = b1ddi.create("/dns/auth_nsg", body=json.dumps(ansgBody))
    if response.status_code == 200:
        nsg_response = response.json()
        table = PrettyTable()
        table.field_names = [
            "Name",
            "Comment",
            "ID",
            "External Primaries",
            "NIOS-X Host",
            "NSG",
            "Tags",
        ]
        table.add_row(
            [
                nsg_response["result"]["name"],
                nsg_response["result"]["comment"],
                nsg_response["result"]["id"],
                nsg_response["result"]["external_primaries"],
                nsg_response["result"]["internal_secondaries"],
                nsg_response["result"]["nsgs"],
                nsg_response["result"]["tags"],
            ]
        )
        print(table)
    else:
        print(response.status_code, response.text)


def delete_auth_nsg(b1ddi, ansgid):
    response = b1ddi.delete("/dns/auth_nsg", id=ansgid)
    if response.status_code == 200:
        print("{} has been deleted successfully".format(ansgid))
    else:
        print(response.status_code, response.text)


if __name__ == "__main__":
    main()
