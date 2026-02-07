import subprocess

from casual.performance.test.configuration import Configuration
from casual.performance.test.casual import scale_instance, scale_queue_forward

def runner():
    config = Configuration("runner")
    return config


def get_domains(parameters: dict = {}):
    return {
        "runner": runner()
    }


def test_setup():
    pass


def test_shutdown():
    pass

def test_stage(num_calls: int, payload_size: int):
    rc = subprocess.run(f'./tpcall-client -n {num_calls} -p {payload_size} -s casual/example/echo', shell=True)


def test_run(parameters: dict = {}):
    print(f'Running test with config: {parameters}')
    # runtime = parameters.get('runtime', 30)
    test_stage(10000, 128)
    test_stage(10000, 1024)
    test_stage(10000, 4096)
    test_stage(10000, 16384)

