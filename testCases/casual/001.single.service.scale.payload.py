from locust import FastHttpUser, task, events
import base64
import requests
import os
from casual.performance.test import telegraf
from casual.performance.test import casual
from casual.performance.test import helpers
import inspect

import user_config

###########################################################################################################
#
# Global declarations needed in locust testfiles

starttime=float()
configuration={}

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

   # Note the double ${{}} to escape f-string functionality
   return {
            "name" : name,
            "home" : home,
            "remote" : user_config.remote( name),
            "files" : 
            [
               {
                  "filename" : "configuration/domain.yaml",
                  "content" : f"""
domain:
  name: {name}

  servers:
    - alias: casual-example-server
      path: ${{CASUAL_HOME}}/example/bin/casual-example-server
      instances: 1
      arguments:
        - --sleep 
        - 2s

  executables:
    - alias: casual-http-inbound
      path: ${{CASUAL_HOME}}/nginx/sbin/nginx
      arguments: 
        - "-c" 
        - ${{CASUAL_DOMAIN_HOME}}/configuration/nginx.conf
        - "-p"
        - ${{CASUAL_DOMAIN_HOME}}

    - alias: casual-event-service-log
      path: ${{CASUAL_HOME}}/bin/casual-event-service-log
      arguments: [ --file, logs/statistics.log ]

"""
               }
            ],
            "nginx_port" : user_config.port( name)
         }


@events.test_start.add_listener
def on_test_start( environment, **kwargs):
   global starttime
   global configuration

   base = casual.make_base()

   configuration = {
      "domains": 
      [
         telegraf.config( base, "telegraf", user_config.remote( "telegraf")),
         domainX( base, environment)
      ]
   }

   casual.on_test_start( configuration, environment)
   starttime = helpers.write_start_information( configuration, environment)

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
   global starttime
   global configuration

   casual.on_test_stop( configuration, environment)

   helpers.write_stop_information( configuration, environment, starttime)

