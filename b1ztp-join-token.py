#!/usr/bin/env python3

import bloxone
import json
from prettytable import PrettyTable
import click


@click.command()
@click.option(
    "-l", "--list", is_flag=True, default=False, help="List current join tokens"
)
@click.option("-c", "--create", is_flag=True, default=False, help="Create join token")
@click.option("-d", "--delete", is_flag=True, default=False, help="Delete join token")
@click.option("-i", "--id", type=str, help="Join Token ID")
@click.option(
    "-t",
    "--tokens",
    multiple=True,
    help="Provide multiple IDs to delete a list of join tokens",
)
def main(list, create, delete, id, tokens):
    b1ztp = bloxone.b1ztp("b1config.ini")
    if list:
        if id:
            response = b1ztp.get("/jointoken", id=id)
        else:
            response = b1ztp.get("/jointoken")
        if response.status_code == 200:
            list_token(response.json())
        else:
            print(response.status_code, response.text)

    if create:
        # Collect name and description information from user
        name = input("UDDI Join Token Name:")
        description = input("UDDI Join Token Description:")
        jToken = {"name": name, "description": description}
        # Create token
        response = b1ztp.create("/jointoken", body=json.dumps(jToken))
        if response.status_code == 201:
            create_token(response.json())
        else:
            print(response.status_code, response.text)

    if delete:
        if id:
            response = b1ztp.delete("/jointoken", id=id)
        else:
            response = b1ztp.delete("/jointokens")
        if response.status_code == 204:
            print("{} deleted successfully".format(id))
        else:
            print(response.status_code, response.text)


def list_token(response):
    table = PrettyTable()
    joinToken = response
    # print(response)
    table.field_names = ["ID", "Last Used", "Name", "Status", "Token ID", "Use Counter"]
    for x in joinToken["results"]:
        if "last_used_at" in x:
            table.add_row(
                [
                    x["id"],
                    x["last_used_at"],
                    x["name"],
                    x["status"],
                    x["token_id"],
                    x["use_counter"],
                ]
            )
        else:
            table.add_row(
                [
                    x["id"],
                    "Unused",
                    x["name"],
                    x["status"],
                    x["token_id"],
                    x["use_counter"],
                ]
            )
    print(table)


def create_token(response):
    table = PrettyTable()
    createToken = response
    table.field_names = [
        "Join Token",
        "Token ID",
        "ID",
        "Name",
        "Description",
        "Use Counter",
    ]
    table.add_row(
        [
            createToken["join_token"],
            createToken["result"]["token_id"],
            createToken["result"]["id"],
            createToken["result"]["name"],
            createToken["result"]["description"],
            createToken["result"]["use_counter"],
        ]
    )
    print(table)


if __name__ == "__main__":
    main()
