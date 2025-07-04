import base64
import requests
import time


from casual.performance.test.configuration import Configuration, InboundConnection, Discovery, OutboundGroupList, OutboundGroup, OutboundConnection, OutboundConnectionList

def domainx():
    config = Configuration( "domainx", example_servers=False)

    # gateway
    config.domain.gateway.inbound.groups.append("inbound").connections.append( InboundConnection("0.0.0.0:7772", Discovery(True)))

    return config


def domainy():
    config = Configuration( "domainy")

    # sleep/work service
    config.domain.servers.find_first('casual-example-server').arguments = ['--sleep', '5ms', '--work', '5ms']

    # gateway
    config.domain.gateway.inbound.groups.append("inbound").connections.append("0.0.0.0:7772")

    return config


def runner():
    config = Configuration("runner", example_servers=False)

    return config


def get_domains(parameters: dict = {}):
    return {
        "domainx": domainx(),
        "domainy": domainy(),
        "runner": runner()
    }


def test_setup():
    pass


def test_shutdown():
    pass


# def _get_domain_configuration(domain: str):
#     response = requests.post(
#         url = f"http://{domain}:8080/casual/.casual/domain/configuration/get",
#         json = {},
#         headers = { "content-type": "application/json"}
#     )

def _set_domain_config(domain: str, data: str):
    if domain == 'runner':
        host = 'localhost'
    else:
        host = domain
    requests.post(
        url = f"http://{host}:8080/casual/.casual/domain/configuration/post",
        data = data,
        headers = { "content-type": "application/json"}
    )


def _set_outbound_connections(src_domain: str, dst_domain: str, instances: int):
    cfg = get_domains()[src_domain]
    _set_domain_config(src_domain, cfg.as_json())

    print("default config applied.")
    time.sleep(3.0)

    cfg.domain.gateway.outbound.groups.append("outbound").connections = OutboundConnectionList([OutboundConnection(address=f"{dst_domain}:7772")] * instances)

    data = cfg.as_json()
    print(f"data: {data}")
    _set_domain_config(src_domain, data)


payload = base64.b64encode( bytes(1024))


def test_stage(instances: int, stage_time: float):
    import casual.server.api
    from casual.server.exception import CallError
    
    _set_outbound_connections("runner", "domainx", instances)
    _set_outbound_connections("domainx", "domainy", instances)
    
    time.sleep(2)

    start = time.time()
    done = False
    while not done:
        for _ in range(100):
            try:
                casual.server.api.call('casual/example/echo', payload)
                time.sleep(0.01)
            except CallError:
                # just ignore errors for now
                pass
        now = time.time()
        done = (now - start) > stage_time


def test_run(parameters: dict = {}):
    print(f'Running test with config: {parameters}')
    runtime = parameters.get('runtime', 30)
    stage_time = float(runtime) / 3
    test_stage(100, stage_time)
    test_stage(250, stage_time)
    test_stage(450, stage_time)
    with open("/home/casual/logs/casual.log") as logfile:
        print(logfile.read())

