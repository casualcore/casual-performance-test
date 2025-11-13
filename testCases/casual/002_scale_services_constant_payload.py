from locust import FastHttpUser, events, task
from locust.env import Environment
from locust.log import setup_logging
from locust.stats import stats_history, stats_printer

import base64
import gevent

from casual.performance.test.configuration import Configuration

global_10K = base64.b64encode( bytes( 10 * 1024))

setup_logging("INFO")

class TestCase( FastHttpUser):
    """ Scale services constant payload """

    @task
    def task1( self):
        self.client.post(
            "/casual/example/echo",
            name = "10K",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_10K)

def domainx():
    config = Configuration( "domainx")
    config.domain.servers.find_first("casual-example-server").instances = 10
    return config


def local():
    config = Configuration("runner")
    return config


def get_domains(parameters: dict = {}):
    return {
        "domainx": domainx(),
        "runner": local()
    }

def test_setup():
    pass


def test_shutdown():
    pass


def test_run(parameters: dict):
    print(f'Running test with config: {parameters}')
    env = Environment(user_classes=[TestCase], events=events)
    env.host = "http://domainx:8080/casual"
    runner = env.create_local_runner()

    gevent.spawn(stats_printer(env.stats))
    gevent.spawn(stats_history, env.runner)

    # start the test
    runner.start(10, spawn_rate=1)
    gevent.spawn_later(parameters.get('runtime', 30), runner.quit)

    runner.greenlet.join()
