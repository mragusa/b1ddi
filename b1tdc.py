#!/usr/bin/env python3

import bloxone
import click
from prettytable import PrettyTable

# TODO 
# Add Table for access_codes, app_approvals, application_filters, block_approvals, category_filters, content_categories
# internal_domain_lists, named_lists, network_lists, security_policy_rules
#
# FIX
# adjust table for security_policies to allow rule content to print properly

@click.command()
@click.option("-c", "--config", default="b1config.ini", help="Path to b1config file")
@click.option(
    "-g",
    "--get",
    type=click.Choice(
        [
            "access_codes",
            "app_approvals",
            "application_filters",
            "block_approvals",
            "category_filters",
            "content_categories",
            "internal_domain_lists",
            "named_lists",
            "network_lists",
            "pop_regions",
            "security_policies",
            "security_policy_rules",
            "threat_feeds",
        ],
        case_sensitive=True,
    ),
)
def main(config: str, get: str):
    # B1TDC objects paths stored inside of a dictionary
    b1tdc_objects = {
        "access_codes": "/access_codes",
        "app_approvals": "/app_approvals",
        "application_filters": "/application_filters",
        "block_approvals": "/block_approvals",
        "category_filters": "/category_filters",
        "content_categories": "/content_categories",
        "internal_domain_lists": "/internal_domain_lists",
        "named_lists": "/named_lists",
        "network_lists": "/network_lists",
        "pop_regions": "/pop_regions",
        "security_policies": "/security_policies",
        "security_policy_rules": "/security_policy_rules",
        "threat_feeds": "/threat_feeds",
    }
    # Retreive configu containing API key
    b1tdc = bloxone.b1tdc(config)
    b1tdc_response = b1tdc.get(b1tdc_objects[get])
    if b1tdc_response.status_code == 200:
        b1_res = b1tdc_response.json()
        #print(b1_res["results"][0]["rules"])
        format_response(get, b1_res["results"])
    else:
        print(b1tdc_response.status_code, b1tdc_response.text)


def format_response(get_object, response):
    table = PrettyTable()
    if get_object == "pop_regions":
        table.field_names = ["Addresses", "ID", "Location", "Region"]
        for x in response:
            table.add_row([x["addresses"], x["id"], x["location"], x["region"]])
    if get_object == "security_policies":
        table.field_names = [
            "Access Codes",
            "Block DNS Rebind Attack",
            "Created Time",
            "Default Action",
            "Default Redirect Name",
            #"Description",
            "DFP Services",
            "DFPS",
            "DOH Enabled",
            "DOH FQDN",
            "ECS",
            "ID",
            "Default",
            "Migration Status",
            "Name",
            "Net Address DFPS",
            "Network Lists",
            "OnPrem Resolve",
            "Precedence",
            "Roaming Device Groups",
            #"Rules",
        ]
        for x in response:
            table.add_row(
                [
                    x["access_codes"],
                    x["block_dns_rebind_attack"],
                    x["created_time"],
                    x["default_action"],
                    x["default_redirect_name"],
                    #x["description"],
                    x["dfp_services"],
                    x["dfps"],
                    x["doh_enabled"],
                    x["doh_fqdn"],
                    x["ecs"],
                    x["id"],
                    x["is_default"],
                    x["migration_status"],
                    x["name"],
                    x["net_address_dfps"],
                    x["network_lists"],
                    x["onprem_resolve"],
                    x["precedence"],
                    x["roaming_device_groups"],
                    #x["rules"],
                ]
            )
    if get_object == "threat_feeds":
        table.field_names = [
            "Confidence Level",
            "Threat Level",
            "Name",
            #"Description",
            #"Key",
            "Legacy",
            "Source",
        ]
        for x in response:
            table.add_row(
                [
                    x["confidence_level"],
                    x["threat_level"],
                    x["name"],
                    #x["description"],
                    #x["key"],
                    x["legacy"],
                    x["source"],
                ]
            )
    print(table)


if __name__ == "__main__":
    main()
