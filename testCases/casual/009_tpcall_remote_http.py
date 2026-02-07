import json
import subprocess

from casual.performance.test.configuration import Configuration
from casual.performance.test.casual import scale_instance, scale_queue_forward

def runner():
    config = Configuration("runner", example_servers=False)

    # Add casual-http-outbound
    config.domain.servers.append(path="${CASUAL_HOME}/bin/casual-http-outbound", alias="casual-http-outbound", arguments=["--configuration-files", "${CASUAL_DOMAIN_HOME}/http_config.json"], instances=0)

    return config


def domainx():
    config = Configuration("domainx")
    return config

def get_domains(parameters: dict = {}):
    return {
        "runner": runner(),
        "domainx": domainx()
    }


def test_setup():
    http_config = {
        "http": {
            "default": {
                "service": {
                    "discard_transaction": True
                }
            },
            "services": [
                { "name": "http/echo", "url": "http://domainx:8080/casual/casual/example/echo"}
            ]
        }
    }
    with open("/home/casual/http_config.json", "w") as file:
        json.dump(http_config, file)
    subprocess.run("casual domain -si casual-http-outbound 1", shell=True)


def test_shutdown():
    pass

def test_stage(num_calls: int, payload_size: int):
    rc = subprocess.run(f'./tpcall-client -n {num_calls} -p {payload_size} -s http/echo', shell=True)


def test_run(parameters: dict = {}):
    print(f'Running test with config: {parameters}')
    # runtime = parameters.get('runtime', 30)
    test_stage(10000, 128)
    test_stage(10000, 1024)
    test_stage(10000, 4096)
    test_stage(10000, 16384)

