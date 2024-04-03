from locust import FastHttpUser, task, events
import base64
import requests
import os
from casual.performance.test import telegraf
from casual.performance.test import casual
from casual.performance.test import helpers
from casual.performance.test import configuration

import inspect

import user_config

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
   """ Scale services constant payload """

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

   config_domain_X = configuration.Configuration( name)
   config_domain_X.domain.servers.find_first("casual-example-server").instances = 10

   return {
            "name" : name,
            "home" : home,
            "remote" : user_config.get( name),
            "files" : 
            [
                config_domain_X.configuration_file_entry()
            ],
            "nginx_port" : user_config.port( name)
         }

@events.test_start.add_listener
def on_test_start( environment, **kwargs):
   global starttime
   global stored_configuration

   base = casual.make_base()

   stored_configuration = {
      "domains": 
      [
         telegraf.config( base, "telegrafA", user_config.get( "telegrafA")),
         domainX( base, environment)
      ]
   }

   casual.on_test_start( stored_configuration, environment)
   starttime = helpers.write_start_information( stored_configuration, environment)

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
   global starttime
   global stored_configuration

   casual.on_test_stop( stored_configuration, environment)

   helpers.write_stop_information( stored_configuration, environment, starttime)

