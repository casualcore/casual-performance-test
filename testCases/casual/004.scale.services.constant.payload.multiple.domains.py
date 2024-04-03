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

import time
###########################################################################################################
#
# Global declarations needed in locust testfiles

starttime=float()
stored_configuration={}

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--use-remote-nodes", default=False, action='store_true', help="Remote node mode")

###########################################################################################################

global_10K = base64.b64encode( bytes( 10 * 1024))

class TestCase( FastHttpUser):
    """ Scale services constant payload multiple domains """

    @task
    def task1( self):
        self.client.post(
            name = "10K",
            url = "/casual/example/echo",
            headers = { "content-type": "application/casual-x-octet"},
            data = global_10K)


def domainX( base: str, environment: dict):
    """
    domain definition for a testdomain
    """

    # Use name of function as name of domain
    name = inspect.currentframe().f_code.co_name
    home = os.path.join( base, name)

    config_domain_X = configuration.Configuration( name, example_server = False)
    config_domain_X.domain.gateway.outbound.groups.append("outbound").connections.append( 
          lookup.host("domainY")["gateway_inbound_address"]
    )

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

def domainY( base: str, environment: dict):
    """
    domain definition for a testdomain
    """

    # Use name of function as name of domain
    name = inspect.currentframe().f_code.co_name
    home = os.path.join( base, name)

    config_domain_Y = configuration.Configuration( name)
    config_domain_Y.domain.gateway.inbound.groups.append("inbound").connections.append( 
        lookup.host("domainY")["gateway_inbound_address"]
    )
   
    config_domain_Y.domain.servers.find_first("casual-example-server").instances = 10

    return {
            "name" : name,
            "home" : home,
             "lookup" : {
                "host": lookup.host( "hostB"),
                "domain" : lookup.domain( name)
            },
            "files" : 
            [
                config_domain_Y.configuration_file_entry()
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
            telegraf.config( base, "telegrafB", lookup.domain( "telegrafB"), lookup.host( "hostB") ),

            domainX( base, environment),
            domainY( base, environment)
        ]
    }

    # Set correct host in environment in order to get locust to do its job
    environment.host = lookup.url_prefix( domain_name="domainX", host_alias="hostA")

    casual.on_test_start( configuration, environment)
    starttime = helpers.write_start_information( configuration, environment)
    time.sleep(5)

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
    global starttime
    global stored_configuration

    casual.on_test_stop( stored_configuration, environment)

    helpers.write_stop_information( stored_configuration, environment, starttime)
      
