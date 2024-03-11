from pathlib import Path
import requests
import os
import tempfile
import time
import base64
from locust.env import Environment
from casual.performance.test import helpers
from casual.performance.test import telegraf



def metrics( configuration: dict, environment: dict):

   host = environment.host
   csv_prefix = environment.parsed_options.csv_prefix

   for domain in configuration.get("domains", {}):
      if 'casual_statistics' in domain and domain['casual_statistics'] == False:
         continue

      domain_reply = requests.post(
         url = host + "/.casual/domain/state",
         headers = { "content-type": "application/json"}
      )
      service_reply = requests.post(
         url = host + "/.casual/service/state",
         headers = { "content-type": "application/json"}
      )
      transaction_reply = requests.post(
         url = host + "/.casual/transaction/state",
         headers = { "content-type": "application/json"}
      )

      file_prefix = csv_prefix + "_" + domain['name']
      # Domain metrics
      with open( file_prefix + "_domain.metrics.json", "w") as file:
         file.write( domain_reply.text)

      # Service metrics
      with open( file_prefix + "_service.metrics.json", "w") as file:
         file.write( service_reply.text)

      # Transaction metrics
      with open( file_prefix + "_transaction.metrics.json", "w") as file:
         file.write( transaction_reply.text)

      if 'remote' in domain and 'type' in domain['remote'] and domain['remote']['type'] == "casual":
        if not environment.parsed_options.use_remote_nodes:
          os.system( f"cp {domain['home']}/logs/statistics.log {csv_prefix}_{domain['name']}_statistics.log")

        else:
          destination = domain['remote']['user'] + "@" + domain['remote']['host']

          if destination:
            os.system( f"scp {destination}/logs/statistics.log {csv_prefix}_{domain['name']}_statistics.log")



def reset_metrics( configuration, environment):
   for domain in configuration.get("domains", {}):
      if domain['remote']['type'] == "casual":   
         requests.post(
            url = domain['remote']['url_prefix'] + "/.casual/service/metric/reset",
            headers = { "content-type": "application/json"}
         )

def information( configuration, environment):
   for domain in configuration.get("domains", {}): 
      if domain['remote']['type'] == "casual":
         domain_reply = requests.post(
            url = domain['remote']['url_prefix'] + "/.casual/domain/state",
            headers = { "content-type": "application/json"}
         )

         if not domain_reply:
            print( domain_reply)
            raise SystemError("Could not reach casualdomain!")

         reply = domain_reply.json()

         domain['information'] = {
            "version": reply["result"]["version"]["casual"],
            "commit": reply["result"]["version"]["commit"]
         }


def on_test_start( configuration: dict, environment: Environment):

   setup_domains( configuration, environment)
   start_domains( configuration, environment)

   information( configuration, environment)

   for domain in configuration.get("domains", {}):
      if domain['remote']['type'] == "casual":

         # Warm up
         for i in range( 10):
            requests.post(
               url = domain['remote']['url_prefix'] + "/casual/example/echo",
               headers = { "content-type": "application/casual-x-octet"},
               data = base64.b64encode( bytes( 1 * 1024))
            )

   # Reset casual metrics
   reset_metrics( configuration, environment)

def on_test_stop( configuration, environment):

   metrics( configuration, environment)
   # Get telegraf metrics
   telegraf.metrics( configuration, environment)
 
   stop_domains( configuration, environment)
   remove_domains( configuration, environment)


def make_base():
   return tempfile.mkdtemp(dir="/var/tmp")

def make_home( home: str):
   os.makedirs( os.path.join( home, "configuration" ))
   os.makedirs( os.path.join( home, "logs" ))

def setup_domains( configuration: dict, environment: Environment):
   
   for domain in configuration.get("domains", {}):
      make_home( domain['home'])

      default_domain_env = True

      for configuration_file in domain.get("files",[]):
         default_domain_env = False if configuration_file["filename"] == "domain.env" else default_domain_env
         with open( f"{domain['home']}/{configuration_file['filename']}", 'w') as file:
            file.write( configuration_file["content"])
            file.write( "\n")

      if default_domain_env:
         with open( f"{domain['home']}/domain.env", 'w') as file:
            file.write( f"""
export CASUAL_HOME=$HOME/usr/local/casual
export PATH=$CASUAL_HOME/bin:$PATH 
export LD_LIBRARY_PATH=$CASUAL_HOME/lib:$LD_LIBRARY_PATH

# CASUAL_DOMAIN_HOME - this domain
export CASUAL_DOMAIN_HOME={domain['home']}

# Defines what will be logged.
export CASUAL_LOG='.*'

""")
            file.write( '\n')
      else:
         # append correct CASUAL_DOMAIN_HOME
         with open( f"{domain['home']}/domain.env", 'a') as file:
            file.write( f"""
export CASUAL_DOMAIN_HOME={domain['home']}

""")

      # create nginx-file
      if 'nginx_port' in domain:
         with open( f"{domain['home']}/configuration/nginx.conf", 'w') as nginx_file:
            nginx_file.write( f"""
worker_processes  1;
daemon off;

error_log  logs/debug.log  debug;

#
# Set this to correct value
#
env CASUAL_DOMAIN_HOME;
env CASUAL_HOME;

events {{
    worker_connections  100;
}}

http {{
    include       mime.types;
    default_type  application/octet-stream;
    underscores_in_headers on;

    sendfile        on;

    #keepalive_timeout  0;

    client_max_body_size 500M;

    server {{
        listen       {domain['nginx_port']};
        server_name  localhost;
        root   html;
        index  index.html index.htm;

        location / {{
           casual_url_prefix /;
           casual_pass;
        }}

        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {{
            root   html;
        }}

   }}
}}

""")
            nginx_file.write( '\n')

      Path( f"{domain['home']}/configuration/mime.types").touch()

      if environment.parsed_options.use_remote_nodes:
         destination = domain["remote"]["user"] + "@" + domain["remote"]["host"]
         os.system(f"""
            ssh {destination} mkdir -p {domain['home']}
            scp -r {domain['home']}/* {destination}:{domain['home']}
""")

   return configuration

def start_domains( configuration: dict, environment: Environment):

   for domain in configuration.get("domains", {}):
      if not environment.parsed_options.use_remote_nodes:
         os.system(f"""
         cd {domain["home"]}
         . domain.env
         casual domain --boot configuration/domain.yaml
         """)
      else:
         destination = domain["remote"]["user"] + "@" + domain["remote"]["host"]
         os.system(f"""
            ssh {destination} '
            cd {domain["home"]}
            . domain.env
            casual domain --boot configuration/domain.yaml
'
""")

   time.sleep(1.0)

def stop_domains( configuration: dict, environment: Environment):

   for domain in configuration.get("domains", {}):
      if not environment.parsed_options.use_remote_nodes:
         os.system(f"""
         cd {domain["home"]}
         . domain.env
         casual domain --shutdown
         """)
      else:
         destination = domain["remote"]["user"] + "@" + domain["remote"]["host"]
         os.system(f"""
            ssh {destination} '
            cd {domain["home"]}
            . domain.env
            casual domain --shutdown
'
""")

def remove_domains( configuration: dict, environment: Environment):

   for domain in configuration.get("domains", {}):
      if not environment.parsed_options.use_remote_nodes:
         os.system(f"""
         rm -rf {domain["home"]}
         """)
      else:
         destination = domain["remote"]["user"] + "@" + domain["remote"]["host"]
         os.system(f"""
            ssh {destination} '
            rm -rf {domain["home"]}
'
            """)
         os.system(f"""
         rm -rf {domain["home"]}
         """)