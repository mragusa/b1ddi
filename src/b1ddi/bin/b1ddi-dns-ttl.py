#!/usr/bin/env python3

import bloxone
import click
import csv
import json


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
@click.option("-f", "--file", help="Import CSV file")
def main(config: str, file: str):
    """Update B1DDI DNS record TTLs"""
    b1 = bloxone.b1ddi(config)
    with open(file, newline="") as nios_file:
        reader = csv.DictReader(nios_file)
        for row in reader:
            fqdn = row["fqdn*"]
            if row["ttl"]:
                ttl = row["ttl"]
                print(f"Get {fqdn} ID")
                current_record = b1.get_id(
                    "/dns/record",
                    key="dns_absolute_name_spec",
                    value=f"{fqdn}.",
                )
                print(f"Updating {fqdn} TTL {current_record} to {ttl}")
                update_ttl = b1.replace(
                    "/dns/record", id=current_record, body=json.dumps({"ttl": ttl})
                )
                if update_ttl.status_code != 200:
                    print(update_ttl.status_code, update_ttl.text)
                else:
                    print(f"Updated {fqdn} TTL to {ttl}")


if __name__ == "__main__":
    main()
