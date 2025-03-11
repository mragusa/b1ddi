#!/usr/bin/env python3

import bloxone
import click


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
def main(config: str):
    b1 = bloxone.b1ddi(config)
    b1_subnet = b1.get("/dns/acl")
    if b1_subnet.status_code != 200:
        print(b1_subnet.status_code, b1_subnet.text)
    else:
        named_list = b1_subnet.json()
        for x in named_list["results"]:
            for y in x["list"]:
                print(y)


if __name__ == "__main__":
    main()
