from casual.performance.test import lookup


# Setup preconfigured domains based on provided domain configuration file
# Note that domain <--> host mapping cannot be generated but has to be provided by the testcase
def preconfigured_jca_domains():
    domains = []
    for domain in lookup.domains():
        if domain["type"] == "jca":
            domains.append(
                {
                    "name": domain["name"],
                    "home": None,
                    "lookup": {
                        "host": None,
                        "domain": domain
                    },
                    "casual_statistics": False,
                    "files": []
                }
            )
    return domains


def has_name(name):
    return lambda dc: dc['name'] == name


# Cannot build jca domains, only use preconfigured domains
def config(domain_name: str, host_alias: str):
    dc = next( filter( has_name(domain_name), preconfigured_jca_domains()), None)
    if dc is not None:
        dc["lookup"]["host"] = lookup.host(host_alias)
    return dc


def metrics(domain: dict, csv_prefix: str):
    pass


def information(domain: dict):
    pass


def warmup(domain: dict):
    pass


def reset_metrics(domain: dict):
    pass


def setup_domain(domain: dict):
    pass


def start_domain(domain: dict):
    pass


def stop_domain(domain: dict):
    pass
