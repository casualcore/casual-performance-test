import os
import yaml

model = {}

host_config_file = os.getenv("CASUAL_HOST_CONFIG_FILE")
if not host_config_file:
    raise SystemError("CASUAL_HOST_CONFIG_FILE need to be set!")

if not os.path.exists(host_config_file):
    raise SystemError(f"{host_config_file} is missing!")

with open(host_config_file, "r") as file:
    model["hosts"] = yaml.safe_load(file)["hosts"]

domain_config_file = os.getenv("CASUAL_DOMAIN_CONFIG_FILE")
if not domain_config_file:
    raise SystemError("CASUAL_DOMAIN_CONFIG_FILE need to be set!")

if not os.path.exists(domain_config_file):
    raise SystemError(f"{domain_config_file} is missing!")

with open(domain_config_file, "r") as file:
    model["domains"] = yaml.safe_load(file)["domains"]


def domains():
    return model["domains"]


def domain(name):

    for entry in model["domains"]:
        if entry["name"] == name:
            return entry

    raise SystemError(f"{name} is not found in {domain_config_file}")


def host(alias):
    site_name = os.getenv("CASUAL_SITE_NAME")
    if not site_name:
        raise SystemError("CASUAL_SITE_NAME need to be set!")

    for entry in model["hosts"][site_name]:
        if entry["alias"] == alias:
            return entry

    raise SystemError(f"{alias} is not found in {host_config_file}")


def url_prefix(domain_name, host_alias):
    return f"http://{host(host_alias)['hostname']}:{domain(domain_name)['inbound-http-port']}"


def inbound_http_port(name):
    return domain(name)["inbound-http-port"]


def inbound_gateway_port(domain_name):
    return domain(domain_name)['inbound-gateway-port']


def inbound_gateway_address(domain_name, host_alias):
    return (
        f"{host(host_alias)['hostname']}:{domain(domain_name)['inbound-gateway-port']}"
    )
