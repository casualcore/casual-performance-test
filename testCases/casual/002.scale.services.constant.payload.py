from pathlib import Path
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

def domainX( base: str, environment: dict):
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
    csv_prefix = environment.parsed_options.csv_prefix
    testsuite = Path( environment.parsed_options.locustfile).stem

    casual.on_test_start( stored_configuration)
    starttime = helpers.write_start_information( stored_configuration, csv_prefix, testsuite)

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
    global starttime
    global stored_configuration

    csv_prefix = environment.parsed_options.csv_prefix
    testsuite = Path( environment.parsed_options.locustfile).stem

    casual.on_test_stop( stored_configuration, csv_prefix)

    helpers.write_stop_information( stored_configuration, csv_prefix, testsuite, starttime)

