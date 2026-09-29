#!/usr/bin/env python3
# TODO:Add ability to delete ACL and update ACL
# TODO:Update help menu

import bloxone
import click
import json
from rich.console import Console
from rich.table import Table

console = Console()


def get_acl(b1):
    b1_acl = b1.get("/dns/acl")
    if b1_acl.status_code != 200:
        print(b1_acl.status_code, b1_acl.text)
    else:
        named_list = b1_acl.json()
        for x in named_list["results"]:
            table = Table(
                title=x["name"] + " " + x["id"], row_styles=["dim", ""], highlight=True
            )
            table.add_column("Access", justify="center")
            table.add_column("Nested ACL", justify="center")
            table.add_column("Address", justify="center")
            table.add_column("Element", justify="center")
            table.add_column("TSIG", justify="center")
            for y in x["list"]:
                table.add_row(
                    y["access"],
                    y["acl"],
                    y["address"],
                    y["element"],
                    y["tsig_key"],
                )
            console.print(table)


def add_acl(b1, name, aclList):
    aclBody = {"name": name, "list": aclList}
    b1_acl = b1.create("/dns/acl", body=json.dumps(aclBody))
    if b1_acl.status_code != 200:
        print(b1_acl.status_code, b1_acl.text)
    else:
        get_acl(b1)


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="BloxOne DDI Config File"
)
@click.option(
    "-g", "--get", is_flag=True, default=False, help="Get Named ACL Information"
)
@click.option("-a", "--add", is_flag=True, default=False, help="Add Named ACL")
@click.option(
    "-n", "--name", default="Internal", show_default=False, help="NamedACL Name"
)
@click.option(
    "--address",
    # default=["10.0.0.1 allow"],
    type=(str, str),
    multiple=True,
    show_default=True,
    help="NamedACL Address element",
)
@click.option("--acl", help="Infoblox ACL String")
def main(config: str, get: bool, add: bool, name: str, address: list, acl: str):
    aclList = []
    if address:
        ip_access = dict(address)
        if ip_access:
            for a in ip_access:
                print(a, ip_access[a])
                aclList.append({"address": a, "element": "ip", "access": ip_access[a]})
    if acl:
        acl_list = acl.split(",")
        for a in acl_list:
            access = a.split("/")
            aclList.append(
                {"address": access[0], "element": "ip", "access": access[1].lower()}
            )
    b1 = bloxone.b1ddi(config)
    if get:
        get_acl(b1)
    if add:
        add_acl(b1, name, aclList)


if __name__ == "__main__":
    main()
