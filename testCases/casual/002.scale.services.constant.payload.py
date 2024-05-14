import base64
import inspect
import os
from pathlib import Path

from casual.performance.test import configuration, helpers, lookup, telegraf
from locust import FastHttpUser, events, task

###########################################################################################################
#
# Global declarations needed in locust testfiles

starttime=float()
stored_configuration={}

###########################################################################################################

global_10K = base64.b64encode( bytes( 10 * 1024))

class TestCase( FastHttpUser):
    """ Scale services constant payload """

    @task
    def task1( self):
        self.client.post(
            "/casual/example/echo",
            name = "10K",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_10K)

def domainX( base: str, host_alias: str):
    """
    domain definition for a testdomain
    """

    # Use name of function as name of domain
    name = inspect.currentframe().f_code.co_name
    home = os.path.join( base, name)

    config_domain_X = configuration.Configuration( name)
    config_domain_X.domain.servers.find_first("casual-example-server").instances = 10

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

@events.test_start.add_listener
def on_test_start( environment, **kwargs):
    global starttime
    global stored_configuration

    base = helpers.make_base()

    stored_configuration = {
        "domains": 
        [
            telegraf.config( base, "telegrafA", "hostA"),
            domainX( base, "hostA")
        ]
    }

    # Set correct host in environment in order to get locust to do its job
    environment.host = lookup.url_prefix( domain_name="domainX", host_alias="hostA")
    csv_prefix = environment.parsed_options.csv_prefix
    testsuite = Path( environment.parsed_options.locustfile).stem

    helpers.on_test_start( stored_configuration)
    starttime = helpers.write_start_information( csv_prefix, testsuite)

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
    global starttime
    global stored_configuration

    csv_prefix = environment.parsed_options.csv_prefix
    testsuite = Path( environment.parsed_options.locustfile).stem

    helpers.on_test_stop( stored_configuration, csv_prefix)
    helpers.write_stop_information( stored_configuration, csv_prefix, testsuite, starttime)

