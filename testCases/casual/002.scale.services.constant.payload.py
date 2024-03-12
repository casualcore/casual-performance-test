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

   # Note the double ${{}} to escape f-string functionality
   return {
            "name" : name,
            "home" : home,
            "remote" : user_config.get( name),
            "files" : 
            [
               {
                  "filename" : "configuration/domain.yaml",
                  "content" : f"""
system:
  resources:
    - key: "rm-mockup"
      server: "rm-proxy-casual-mockup"
      xa_struct_name: "casual_mockup_xa_switch_static"
      libraries:
        - "casual-mockup-rm"
      paths:
        library:
          - "${{CASUAL_HOME}}/lib"

domain:
  name: {name}

  transaction:
    resources:
      - name: example-resource-server
        key: rm-mockup
        instances: 2

  servers:
    - alias: casual-example-server
      path: ${{CASUAL_HOME}}/example/bin/casual-example-server
      instances: 10

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
      instances: 1

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
         telegraf.config( base, "telegrafA", user_config.get( "telegrafA")),
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

