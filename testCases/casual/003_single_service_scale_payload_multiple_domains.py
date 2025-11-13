from locust import FastHttpUser, events, task
from locust.env import Environment
from locust.log import setup_logging
from locust.stats import stats_history, stats_printer

import base64
import gevent

from casual.performance.test.configuration import Configuration

global_1B = base64.b64encode( bytes( 1))
global_1K = base64.b64encode( bytes( 1 * 1024))
global_10K = base64.b64encode( bytes( 10 * 1024))
global_100K = base64.b64encode( bytes( 100 * 1024))

setup_logging("INFO")

class TestCase( FastHttpUser):
    """ Single service scale payload multiple domains """

    @task
    def task1( self):
        self.client.post(
            "/casual/example/echo",
            name = "1B",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_1B)

    @task
    def task2( self):
        self.client.post(
            "/casual/example/echo",
            name = "1K",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_1K)

    @task
    def task3( self):
        self.client.post(
            "/casual/example/echo",
            name = "10K",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_10K)

    @task
    def task4( self):
        self.client.post(
            "/casual/example/echo",
            name = "100K",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_100K)

def domainx():
    """
    domain definition for a testdomain
    """

    config = Configuration("domainx", example_servers = False)
    config.domain.gateway.outbound.groups.append("outbound").connections.append("domainy:7772")

    return config


def domainy():
    """
    domain definition for a testdomain
    """

    config = Configuration("domainy")
    config.domain.gateway.inbound.groups.append("inbound").connections.append("0.0.0.0:7772")

    return config


def local():
    return Configuration("runner")


def get_domains(parameters: dict = {}):
    return {
        "domainx": domainx(),
        "domainy": domainy(),
        "runner": local()
    }


def test_setup():
    pass


def test_shutdown():
    pass


def test_run(parameters: dict = {}):
    print(f'Running test with config: {parameters}')
    env = Environment(user_classes=[TestCase], events=events)
    env.host = "http://domainx:8080/casual"
    runner = env.create_local_runner()

    gevent.spawn(stats_printer(env.stats))
    gevent.spawn(stats_history, env.runner)

    # start the test
    runner.start(1, spawn_rate=1)
    gevent.spawn_later(parameters.get('runtime', 30), runner.quit)

    runner.greenlet.join()
      
