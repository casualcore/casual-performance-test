import base64
import inspect
import os
import time
from pathlib import Path

from casual.performance.test import configuration, helpers, lookup, telegraf
from locust import FastHttpUser, events, task

###########################################################################################################
#
# Global declarations needed in locust testfiles

starttime=float()
stored_configuration={}

###########################################################################################################

global_1B = base64.b64encode( bytes( 1))
global_1K = base64.b64encode( bytes( 1 * 1024))
global_10K = base64.b64encode( bytes( 10 * 1024))
global_100K = base64.b64encode( bytes( 100 * 1024))

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

def domainX( base: str, host_alias: str):
    """
    domain definition for a testdomain
    """

    # Use name of function as name of domain
    name = inspect.currentframe().f_code.co_name
    home = os.path.join( base, name)

    config_domain_X = configuration.Configuration( name, example_server = False)
    config_domain_X.domain.gateway.outbound.groups.append("outbound").connections.append( 
        lookup.inbound_gateway_address( "domainY", "hostB")
    )

    return {
            "name" : name,
            "home" : home,
            "lookup" : {
                "host": lookup.host( host_alias),
                "domain" : lookup.domain( name)
            },
            "files" : 
            [
                config_domain_X.configuration_file_entry()
            ],
            "nginx_port" : lookup.inbound_http_port( name)
        }

def domainY( base: str, host_alias: str):
    """
    domain definition for a testdomain
    """

    # Use name of function as name of domain
    name = inspect.currentframe().f_code.co_name
    home = os.path.join( base, name)

    config_domain_Y = configuration.Configuration( name)
    config_domain_Y.domain.gateway.inbound.groups.append("inbound").connections.append( 
        lookup.inbound_gateway_address( "domainY", host_alias)
    )

    return {
            "name" : name,
            "home" : home,
            "lookup" : {
                "host": lookup.host( host_alias),
                "domain" : lookup.domain( name)
            },
            "files" : 
            [
                config_domain_Y.configuration_file_entry()
            ],
            "nginx_port" : lookup.inbound_http_port( name)
        }


@events.test_start.add_listener
def on_test_start( environment, **kwargs):
    global starttime
    global stored_configuration

    base = helpers.make_base()

    stored_configuration = {
        "domains": 
        [
            telegraf.config( base, "telegrafA", "hostA"),
            telegraf.config( base, "telegrafB", "hostB"),

            domainX( base, "hostA"),
            domainY( base, "hostB")
        ]
    }

    # Set correct host in environment in order to get locust to do its job
    environment.host = lookup.url_prefix( domain_name="domainX", host_alias="hostA")
    csv_prefix = environment.parsed_options.csv_prefix
    testsuite = Path( environment.parsed_options.locustfile).stem

    helpers.on_test_start( stored_configuration)
    starttime = helpers.write_start_information( csv_prefix, testsuite)

    time.sleep(5)

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
    global starttime
    global stored_configuration

    csv_prefix = environment.parsed_options.csv_prefix
    testsuite = Path( environment.parsed_options.locustfile).stem

    helpers.on_test_stop( stored_configuration, csv_prefix)
    helpers.write_stop_information( csv_prefix, testsuite, starttime)
      
