#!/usr/bin/env python3

import csv
import bloxone
from prettytable import PrettyTable
import click
from click_option_group import optgroup


@click.command()
@optgroup.group("Required Options")
@optgroup.option(
    "--config", type=str, default="b1config.ini", help="B1DDI Configuration INI file"
)
@optgroup.group("Batch Operations")
@optgroup.option(
    "-f", "--file", type=str, help="CSV file containing data for processing"
)
@optgroup.group("B1TD NamedList Actions")
@optgroup.option(
    "-l",
    "--listnl",
    is_flag=True,
    help="Use this method to retrieve information on all Named List objects for the account. Note that list items are not returned for this operation",
)
@optgroup.option(
    "-c",
    "--create",
    is_flag=True,
    help="Use this method to create a Named List object.",
)
@optgroup.option(
    "-d",
    "--delete",
    is_flag=True,
    help="Use this method to delete Named List objects. Deletion of multiple lists is an all-or-nothing operation (if any of the specified lists can not be deleted then none of the specified lists will be deleted).",
)
@optgroup.option(
    "-p",
    "--patch",
    is_flag=True,
    help="Use this method to insert items for multiple Named List objects. Note that duplicated items correspondig to named list are silently skipped and only new items are appended to the named list. Note that DNSM, TI, Fast Flux and DGA lists cannot be updated. Only named lists of Custom List type can be updated by this operation. If one or more of the list ids is invalid, or the list is of invalid type then the entire operation will be failed.  The Custom List Items represent the list of the FQDN or IPv4 addresses to define whitelists and blacklists for additional protection.",
)
@optgroup.group("B1TD NamedList Fields")
@optgroup.option(
    "-n", "--name", type=str, help="The identifier for a Named List object."
)
@optgroup.option(
    "-i", "--item", type=str, help="Add the item in the custom list using this field."
)
@optgroup.option(
    "--comment",
    help="Add the description/comments to each item in the custom list using this field.",
)
@optgroup.option(
    "--confidence",
    default="HIGH",
    type=click.Choice(["LOW", "MEDIUM", "HIGH"]),
    help="Confidence level of item",
)
def main(config, file, listnl, create, delete, patch, name, comment, item, confidence):
    # Consume b1ddi ini file for login
    b1tdc = bloxone.b1tdc(config)
    print("API Key: {}".format(b1tdc.api_key))
    print("API Version: {}".format(b1tdc.api_version))

    if listnl:
        if name:
            try:
                response = b1tdc.get_custom_list(name)
            except Exception as e:
                print(e)
            named_list(response)
        else:
            try:
                response = b1tdc.get_custom_lists()
            except Exception as e:
                print(e)
            get_named_list(response)
    if create:
        try:
            response = b1tdc.create_custom_list(
                name,
                confidence,
                items_described=[{"description": comment, "item": item}],
            )
        except Exception as e:
            print(e)
        named_list(response)

    if delete:
        if item and comment:
            try:
                response = b1tdc.delete_items_from_custom_list(
                    name, items_described=[{"description": comment, "item": item}]
                )
            except Exception as e:
                print(e)
            if response.status_code == 204:
                print("{} deleted from {}".format(item, name))
                response = b1tdc.get_custom_list(name)
                named_list(response)
            else:
                print(response.status_code, response.text)
        elif name:
            try:
                response = b1tdc.delete_custom_lists(names=[name])
            except Exception as e:
                print(e)
            if response.status_code == 204:
                print("{} list deleted".format(name))
            else:
                print(response.status_code, response.text)
        else:
            print("Invalid Flags Specified")

    if patch:
        try:
            response = b1tdc.add_items_to_custom_list(
                name, items_described=[{"description": comment, "item": item}]
            )
        except Exception as e:
            print(e)
        if response.status_code == 201:
            print("{} update successful".format(name))
            response = b1tdc.get_custom_list(name)
            named_list(response)
        else:
            print(response.status_code, response.text)

    if file:
        with open(file, newline="") as csvfile:
            b1tdcfile = csv.reader(csvfile, delimiter=",")
            for row in b1tdcfile:
                if row[0] == "create":
                    response = b1tdc.create_custom_list(
                        row[1],
                        confidence,
                        items_described=[{"description": row[2], "item": row[3]}],
                    )
                if row[0] == "update":
                    response = b1tdc.add_items_to_custom_list(
                        row[1],
                        items_described=[{"description": row[2], "item": row[3]}],
                    )
                if row[0] == "deleteitem":
                    response = b1tdc.delete_items_from_custom_list(
                        row[1],
                        items_described=[{"description": row[2], "item": row[3]}],
                    )
                if row[0] == "delete":
                    response = b1tdc.delete_custom_lists(names=[row[1]])

                if (
                    response.status_code == 200
                    or response.status_code == 201
                    or response.status_code == 204
                ):
                    print("Success")
                else:
                    print(response.status_code, response.text)


def get_named_list(response):
    table = PrettyTable()
    table.field_names = [
        "Confidence Level",
        "Creation Time",
        "Description",
        "ID",
        "Item Count",
        "Name",
        "Policies",
        "Tags",
        "Threat Level",
        "Type",
        "Last Updated",
    ]
    if response.status_code == 200:
        b1tdc_list = response.json()
        for nl in b1tdc_list["results"]:
            table.add_row(
                [
                    *[
                        str(nl[key])
                        for key in [
                            "confidence_level",
                            "created_time",
                            "description",
                            "id",
                            "item_count",
                            "name",
                            "policies",
                            "tags",
                            "threat_level",
                            "type",
                            "updated_time",
                        ]
                    ]
                ]
            )
    else:
        print(response.status_code, response.text)
    print(table)


def named_list(response):
    table = PrettyTable()
    table.field_names = [
        "Confidence Level",
        "Creation Time",
        "Description",
        "ID",
        "Item Count",
        "Items",
        "Items Description",
        "Name",
        "Policies",
        "Tags",
        "Threat Level",
        "Type",
        "Last Updated",
    ]
    if response.status_code == 200 or response.status_code == 201:
        b1tdc_named_list = response.json()
        for nl in b1tdc_named_list["results"]["items_described"]:
            table.add_row(
                [
                    b1tdc_named_list["results"]["confidence_level"],
                    b1tdc_named_list["results"]["created_time"],
                    b1tdc_named_list["results"]["description"],
                    b1tdc_named_list["results"]["id"],
                    b1tdc_named_list["results"]["item_count"],
                    nl["item"],
                    nl["description"],
                    b1tdc_named_list["results"]["name"],
                    b1tdc_named_list["results"]["policies"],
                    b1tdc_named_list["results"]["tags"],
                    b1tdc_named_list["results"]["threat_level"],
                    b1tdc_named_list["results"]["type"],
                    b1tdc_named_list["results"]["updated_time"],
                ]
            )
        print(table)
    else:
        print(response.status_code, response.text)


if __name__ == "__main__":
    main()
