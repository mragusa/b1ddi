#!/usr/bin/env python3

import csv
import json
import bloxone
import click
from click_option_group import optgroup
from rich.console import Console
from rich.table import Table


@click.command()
@optgroup.group("BloxOne Configuration File")
@optgroup.option("-c", "--config", default="b1config.ini", help="BloxOne Ini File")
@optgroup.group("BloxOne DHCP Option Filters")
@optgroup.option("-f", "--file", help="CSV Import File")
def main(config, file):
    b1ddi = bloxone.b1ddi(config)
    get_dhcp_filters(b1ddi)
    # open_file(file)


def get_dhcp_filters(b1ddi):
    response = b1ddi.get("/dhcp/option_filter")
    if response.status_code == 200:
        dhOptFilter = response.json()
        dhOptFilterTable = Table(
            "Created",
            "Name",
            "Comment",
            "DHCP Options: (Code ID, Value)",
            "Bootfile ",
            "Boot Server",
            "Next Server",
            "Rule Match",
            "Rule",
            title="BloxOne DHCP Option Filters",
        )
        print(response.json())
        for x in dhOptFilter["results"]:
            filterRules = []
            filterOptions = []
            for y in x["dhcp_options"]:
                filterOptions.append(
                    "{}, {}".format(y["option_code"], y["option_value"])
                )
            for r in x["rules"]["rules"]:
                filterRules.append(
                    "{}, {}, {}, {}".format(
                        r["compare"],
                        r["option_code"],
                        r["option_value"],
                        r["substring_offset"],
                    )
                )
            dhOptFilterTable.add_row(
                x["created_at"],
                x["name"],
                x["comment"],
                ("\n").join(filterOptions),
                x["header_option_filename"],
                x["header_option_server_name"],
                x["header_option_server_address"],
                x["rules"]["match"],
                str(x["rules"]["rules"]),
            )
        console = Console()
        console.print(dhOptFilterTable)
    else:
        print(response.status_code, response.text)


def create_dhcp_filter(filterRow):
    dhcpOptions = []
    filterRules = []
    dhcpFilterBody = {
        # "name": name,
        # "comment": comment,
        "dhcp_options": dhcpOptions,
        "rules": {"match": "all", "rules": filterRules},
    }
    # for y in filterRow["dhcp_options"]:
    #    print(y)
    # for x in filterRow:
    # print(x)
    # print(filterRow["name"], filterRow["comment"], filterRow["expression"], filterRow["OPTION-60"], filterRow["OPTION-66"], filterRow["OPTION-67"])


def open_file(file):
    with open(file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            create_dhcp_filter(row)


def lookup_dhcp_codes(b1ddi, dhcpOptCode):
    response = b1ddi.get("/dhcp/option_code")
    if response.status_code == 200:
        codeLookup = response.json()
        for x in codeLookup["results"]:
            if x["code"] == dhcpOptCode:
                return x["id"]


if __name__ == "__main__":
    main()
