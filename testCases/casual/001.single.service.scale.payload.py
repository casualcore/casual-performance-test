from locust import FastHttpUser, task, events
import base64
import requests
import os
from casual.performance.test import telegraf
from casual.performance.test import casual
from casual.performance.test import helpers
from casual.performance.test import configuration
from casual.performance.test import lookup

import inspect

###########################################################################################################
#
# Global declarations needed in locust testfiles

starttime=float()
stored_configuration={}

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--use-remote-nodes", default=False, action='store_true', help="Remote node mode")

###########################################################################################################

global_1B = base64.b64encode( bytes( 1))
global_1K = base64.b64encode( bytes( 1 * 1024))
global_10K = base64.b64encode( bytes( 10 * 1024))
global_100K = base64.b64encode( bytes( 100 * 1024))


class TestCase( FastHttpUser):
    """ Single service scale payload """

    @task
    def task1( self):
        self.client.post(
            name = "1B",
            url = "/casual/example/echo",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_1B)

    @task
    def task2( self):
        self.client.post(
            name = "1K",
            url = "/casual/example/echo",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_1K)

    @task
    def task3( self):
        self.client.post(
            name = "10K",
            url = "/casual/example/echo",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_10K)

    @task
    def task4( self):
        self.client.post(
            name = "100K",
            url = "/casual/example/echo",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_100K)

def domainX( base: str, environment: dict):
    """
    domain definition for a testdomain
    """

    # Use name of function as name of domain
    name = inspect.currentframe().f_code.co_name
    home = os.path.join( base, name)

    config_domain_X = configuration.Configuration( name)

    return {
            "name" : name,
            "home" : home,
            "lookup" : {
                "host": lookup.host( "hostA"),
                "domain" : lookup.domain( name)
            },
            "files" : 
            [
                config_domain_X.configuration_file_entry()
            ],
            "nginx_port" : lookup.port( name)
    }


@events.test_start.add_listener
def on_test_start( environment, **kwargs):
    global starttime
    global stored_configuration

    base = casual.make_base()

    stored_configuration = {
        "domains": 
        [
            telegraf.config( base, "telegrafA", lookup.domain( "telegrafA"), lookup.host( "hostA") ),
            domainX( base, environment)
        ]
    }

    # Set correct host in environment in order to get locust to do its job
    environment.host = lookup.url_prefix( domain_name="domainX", host_alias="hostA")

    casual.on_test_start( stored_configuration, environment)
    starttime = helpers.write_start_information( stored_configuration, environment)

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
    global starttime
    global stored_configuration

    casual.on_test_stop( stored_configuration, environment)

    helpers.write_stop_information( stored_configuration, environment, starttime)

