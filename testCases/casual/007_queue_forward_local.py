import base64
import time

from casual.performance.test.configuration import Configuration
from casual.performance.test.casual import scale_instance, scale_queue_forward

def domainx():
    config = Configuration( "domainx")

    # queues
    config.domain.queue.groups.append('test007').queues.append('test007.q1')
    config.domain.queue.forward.groups.append('test007').services.append(source='test007.q1', target='casual/example/sleep')

    # servers
    config.domain.servers.find_first('casual-example-server').arguments = ['--sleep', '50ms', '--work', '20ms']
    config.domain.servers.append(
         path="${CASUAL_HOME}/bin/casual-queue-example-server",
         alias="casual-queue-example-server",
         arguments=["--queues", "test007.q1"],
         instances=1
    )

    # gateway
    config.domain.gateway.inbound.groups.append("inbound").connections.append("0.0.0.0:7772")

    return config


def runner():
    config = Configuration("runner")

    # gateway
    config.domain.gateway.outbound.groups.append("outbound").connections.append("domainx:7772")
    return config


def get_domains(parameters: dict = {}):
    return {
        "domainx": domainx(),
        "runner": runner()
    }


def test_setup():
    pass


def test_shutdown():
    pass


payload = base64.b64encode( bytes(1024))

def _fill_queue(queue: str, num_messages: int):
    import casual.server.api
    for _ in range(num_messages):
        casual.server.api.call(f"casual/example/enqueue/{queue}", payload)

def test_stage(instances: int, stage_time: float):
    scale_queue_forward("domainx", "test007.q1", 0)
    _fill_queue("test007.q1", 1000)
    scale_instance("domainx", "casual-example-server", instances)
    scale_queue_forward("domainx", "test007.q1", instances)
    time.sleep(stage_time)


def test_run(parameters: dict = {}):
    print(f'Running test with config: {parameters}')
    runtime = parameters.get('runtime', 30)
    test_stage(1, float(runtime))

