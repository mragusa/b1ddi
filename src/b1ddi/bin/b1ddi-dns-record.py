#!/usr/bin/env python3

import bloxone
import click


def get_record(b1, type):
    b1_record = b1.get("/dns/record", _filter=f'type=="{type}"', _limit=1000, _offset=0)
    if b1_record.status_code != 200:
        print(b1_record.status_code, b1_record.text)
        return 0
    else:
        return b1_record.json().get("results", [])


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
@click.option("-t", "--type", help="UDDI Record Type")
def main(config: str, type: str):
    """Search for record type and dump out raw json"""
    b1 = bloxone.b1ddi(config)
    tenant_records = get_record(b1, type)
    if tenant_records:
        for r in tenant_records:
            print(r)


if __name__ == "__main__":
    main()
