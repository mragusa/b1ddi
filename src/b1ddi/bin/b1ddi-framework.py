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
    help="Retrieve DNS views",
)
def main(config: str):
    b1 = bloxone.b1ddi(config)
    get_view(b1)


def get_view(b1):
    b1_subnet = b1.get("/ipam/subnet")
    if b1_subnet.status_code != 200:
        print(b1_subnet.status_code, b1_subnet.text)
    else:
        print(b1_subnet.json())


if __name__ == "__main__":
    main()
