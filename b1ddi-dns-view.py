#!/usr/bin/env python3

import bloxone
from rich.console import Console
from rich.table import Table
import click
from click_option_group import optgroup


@click.command()
@optgroup.group("BloxOne Configuration File")
@optgroup.option("-c", "--config", default="b1config.ini", help="BloxOne Ini File")
@optgroup.group("BloxOne DNS Views")
@optgroup.option("-g", "--get", is_flag=True, help="Retreive Current DNS Views")
@optgroup.option("-n", "--new", is_flag=True, help="Create New DNS View")
def main(config, get, new):
    b1ddi = bloxone.b1ddi("b1config.ini")
    if get:
        get_dns_view(b1ddi)


def get_dns_view(b1ddi):
    response = b1ddi.get("/dns/view")
    table = Table(
        "Created", "Name", "ID", "IP Spaces", "Comment", title="BloxOne DNS Views"
    )
    if response.status_code == 200:
        dnsView = response.json()
        ip_space_dns = ""
        ip_spaces_dns = []
        for x in dnsView["results"]:
            if x["ip_spaces"]:
                for i in x["ip_spaces"]:
                    id = i.split("/")
                    if id[2]:
                        ip_spaces_dns.append(get_ip_space(b1ddi, id[2]))
                ip_space_dns = ("\n").join(ip_spaces_dns)
            if not x["comment"]:
                x["comment"] = "None"
            table.add_row(
                x["created_at"], x["name"], x["id"], ip_space_dns, x["comment"]
            )
        console = Console()
        console.print(table)
    else:
        print(response.status_code, response.text)


def get_ip_space(b1ddi, id):
    response = b1ddi.get("/ipam/ip_space", id=id)
    if response.status_code == 200:
        ip_space = response.json()
        return ip_space["result"]["name"]
    else:
        print(response.status_code, response.text)


if __name__ == "__main__":
    main()
