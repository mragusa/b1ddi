#!/usr/bin/env python3


import bloxone
import json
from rich.console import Console
from rich.table import Table
import click
from click_option_group import optgroup


# TODO
# Add functionality for external primaries, external secondaries,  additional options for niosx hosts
# Add functionality for providing tsig keys


@click.command()
@optgroup.group("BloxOne Configuration File")
@optgroup.option(
    "-c", "--config", default="b1config.ini", help="BloxOne Configuration File"
)
@optgroup.group("BloxOne Actions")
@optgroup.option(
    "-g",
    "--get",
    is_flag=True,
    default=False,
    help="Retreive BloxOne Hosts and AuthNSG",
)
@optgroup.option(
    "-n", "--new", is_flag=True, default=False, help="Create BloxOne AuthNSG"
)
@optgroup.option(
    "-d", "--delete", is_flag=True, default=False, help="Delete BloxOne AuthNSG"
)
@optgroup.group("Auth NSG ID")
@optgroup.option("--ansgid", help="Auth NSG ID")
@optgroup.group("BloxOne New AuthNSG Options")
@optgroup.option("--host", multiple=True, default=[], help="BloxOne Host")
@optgroup.option("--ansgname", help="NSG Name")
@optgroup.option("--comment", help="NSG Comment")
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
    response = b1ddi.get("/dns/host")
    if response.status_code == 200:
        # print(response.json())
        table = Table(
            "Address",
            "Name",
            "ID",
            "Comment",
            "Version",
            "Serial Number",
            "Type",
            title="BloxOne DNS Hosts",
        )
        dnsHosts = response.json()
        for x in dnsHosts["results"]:
            # print(x["address"])
            table.add_row(
                x["address"],
                x["name"],
                x["id"],
                x["comment"],
                x["current_version"],
                x["tags"]["host/serial_number"],
                x["type"],
            )
        console = Console()
        console.print(table)
    else:
        print(response.status_code, response.text)


def get_auth_nsg(b1ddi):
    response = b1ddi.get("/dns/auth_nsg")
    if response.status_code == 200:
        authNsg = response.json()
        table = Table(
            "Name",
            "Comment",
            "ID",
            "External Primaries",
            "NIOS-X Host",
            "NSG",
            "Tags",
            title="BloxOne Name Server Groups",
        )
        for x in authNsg["results"]:
            if not x["external_primaries"]:
                x["external_primaries"] = "None"
            if not x["nsgs"]:
                x["nsgs"] = "None"
            if not x["tags"]:
                x["tags"] = "None"
            inS = []
            for s in x["internal_secondaries"]:
                inS.append(s["host"])
            table.add_row(
                x["name"],
                x["comment"],
                x["id"],
                x["external_primaries"],
                "\n".join(inS),
                x["nsgs"],
                x["tags"],
            )
        console = Console()
        console.print(table)
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
        get_auth_nsg(b1ddi)
    else:
        print(response.status_code, response.text)


def delete_auth_nsg(b1ddi, ansgid):
    response = b1ddi.delete("/dns/auth_nsg", id=ansgid)
    if response.status_code == 200:
        print("{} has been deleted successfully".format(ansgid))
        get_auth_nsg(b1ddi)
    else:
        print(response.status_code, response.text)


if __name__ == "__main__":
    main()
