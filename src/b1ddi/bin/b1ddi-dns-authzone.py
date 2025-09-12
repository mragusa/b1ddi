#!/usr/bin/env python3

import bloxone
import click


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
@click.option(
    "-g",
    "--get",
    is_flag=True,
    default=False,
    show_default=True,
    help="Retrieve Auth Zones from B1DDI",
)
def main(config: str, get: bool):
    b1 = bloxone.b1ddi(config)
    if get:
        get_authzone(b1)


def get_authzone(b1):
    b1_authzone = b1.get("/dns/auth_zone")
    if b1_authzone.status_code != 200:
        print(b1_authzone.status_code, b1_authzone.text)
    else:
        auth_zones = b1_authzone.json()
        for az in auth_zones["results"]:
            if az["nsgs"]:
                for n in az["nsgs"]:
                    nsg_path = n.split("/")
                    print(az["id"], az["fqdn"], get_nsgs_name(b1, nsg_path[2]))
            else:
                print(az["id"], az["fqdn"])


def get_nsgs_name(b1, nsgs):
    b1_nsgs = b1.get("/dns/auth_nsg", id=nsgs)
    if b1_nsgs.status_code != 200:
        print(f"Error retreiving nsgs: {b1_nsgs.status_code} {b1_nsgs.text}")
    else:
        nsgs = b1_nsgs.json()
        return nsgs["result"]["name"]


if __name__ == "__main__":
    main()
