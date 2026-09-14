#!/usr/bin/env python3
# TODO finish create user function and testing.
# TODO add user auditing
# TODO add delete user function

import bloxone
import click
from rich.console import Console
from rich.table import Column, Table
from rich import box

console = Console()


def get_user_table(b1):
    b1_users = b1.get_users()
    if b1_users.status_code != 200:
        print(b1_users.status_code, b1_users.text)
    else:
        return b1_users.json().get("results")


def get_group_table(b1):
    uddi_groups = b1.get_groups()
    if uddi_groups.status_code != 200:
        print(uddi_groups.status_code, uddi_groups.text)
    else:
        return uddi_groups.json().get("results")


def create_user(b1):
    full_name = input("Full Name: ")
    user_email = input("Email: ")
    user_groups = input("Groups: ")
    group_list = user_groups.split()
    new_uddi_user = b1.create_user(
        name=full_name,
        email=user_email,
        type="interactive",
        authenticator="IDP",
        groups=[group_list],
    )
    if new_uddi_user.status_code != 200:
        print(new_uddi_user.status_code, new_uddi_user.text)
    else:
        print(f"{full_name}'s Account Created: {user_email}")


def report_user_table(customer, users):
    table = Table(
        Column(header="Name", justify="center"),
        Column(header="Email", justify="center"),
        Column(header="Account ID", justify="center"),
        Column(header="ID", justify="center"),
        Column(header="Sign In Count", justify="center"),
        Column(header="Type", justify="center"),
        Column(header="Created", justify="center"),
        Column(header="Updated", justify="center"),
        Column(header="Confirmation", justify="center"),
        Column(header="Confirmed", justify="center"),
        title=f"BloxOne: {customer} UDDI Users",
        box=box.SIMPLE,
    )
    for u in users:
        if "sign_in_count" in u:
            login_count = u["sign_in_count"]
        else:
            login_count = None
        if "confirmation_sent_at" in u:
            confirmation_email = u["confirmation_sent_at"]
        else:
            confirmation_email = None
        table.add_row(
            u["name"],
            u["email"],
            u["account_id"],
            u["id"],
            str(login_count),
            u["type"],
            u["created_at"],
            u["updated_at"],
            confirmation_email,
            u["confirmed_at"],
        )
    console.print(table)


def report_group_table(customer, uddi_groups):
    group_users = []
    table = Table(
        "Name",
        Column("Description", no_wrap=True),
        "Group ID",
        "Created",
        "Updated",
        Column("Group Users", no_wrap=True),
        title=f"BloxOne: {customer} UDDI Groups",
        box=box.SIMPLE,
    )
    for g in uddi_groups:
        if "users" in g:
            for u in g["users"]:
                if u["approved"]:
                    group_users.append(f'{u["name"]}, {u["type"]}, :white_check_mark:')
                else:
                    group_users.append(
                        f'{u["name"]}, {u["type"]}, :negative_squared_cross_mark:'
                    )
            table.add_row(
                g["name"],
                g["description"],
                g["id"],
                g["created_at"],
                g["updated_at"],
                str("\n".join(group_users)),
            )
        else:
            table.add_row(
                g["name"],
                g["description"],
                g["id"],
                g["created_at"],
                g["updated_at"],
                "None",
            )
    console.print(table)


@click.command()
@click.option(
    "-c",
    "--config",
    default="~/b1ddi/b1config.ini",
    show_default=True,
    help="bloxone ddi config file",
)
@click.option(
    "-l",
    "--list",
    is_flag=True,
    default=False,
    show_default=True,
    help="Retrieve UDDI users/groups",
)
@click.option("--users", is_flag=True, default=False, help="Retrieve UDDI Users")
@click.option("--groups", is_flag=True, default=False, help="Retrieve UDDI Users")
@click.option("--create", is_flag=True, default=False, help="Add UDDI User")
def main(config: str, list: bool, users: bool, groups: bool, create: bool):
    """Infoblox UDDI User Script"""
    b1 = bloxone.b1platform(config)
    customer = b1.get_current_tenant()
    if list:
        if users:
            uddi_users = get_user_table(b1)
            if uddi_users:
                report_user_table(customer, uddi_users)
            else:
                print(f"Unable to retreive {customer} UDDI users")
        if groups:
            uddi_groups = get_group_table(b1)
            if uddi_groups:
                report_group_table(customer, uddi_groups)
    if create:
        create_user(b1)
        uddi_users = get_user_table(b1)
        if uddi_users:
            report_user_table(customer, uddi_users)


if __name__ == "__main__":
    main()
