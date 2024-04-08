from pathlib import Path
import requests
import os
import tempfile
import time
import base64
from casual.performance.test import helpers
from casual.performance.test import telegraf


def url_prefix( lookup: dict):
    prefix = f"http://{lookup['host']['hostname']}:{lookup['domain']['inbound-http-port']}"
    return prefix

def metrics( configuration: dict, csv_prefix: str):
    """
    This is used to fetch casual metrics from domains
    """

    for domain in configuration.get("domains", {}):
        if 'casual_statistics' in domain and domain['casual_statistics'] == False:
            continue

        domain_reply = requests.post(
            url = url_prefix( domain['lookup']) + "/.casual/domain/state",
            headers = { "content-type": "application/json"}
        )
        service_reply = requests.post(
            url = url_prefix( domain['lookup']) + "/.casual/service/state",
            headers = { "content-type": "application/json"}
        )
        transaction_reply = requests.post(
            url = url_prefix( domain['lookup']) + "/.casual/transaction/state",
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

        if domain['lookup']['domain']['type'] == "casual":
            helpers.copy_from_domain('logs/statistics.log', f"{csv_prefix}_{domain['name']}_statistics.log", domain)


def reset_metrics( configuration):
    """
    This is used to reset casual metrics in domains
    """
    for domain in configuration.get("domains", {}):
        if domain['lookup']['domain']['type'] == "casual":   
            requests.post(
                url = url_prefix( domain['lookup']) + "/.casual/service/metric/reset",
                headers = { "content-type": "application/json"}
            )

def information( configuration):
    for domain in configuration.get("domains", {}): 
        if domain['lookup']['domain']['type'] == "casual":
            path = url_prefix( domain['lookup']) + "/.casual/domain/state"
            domain_reply = requests.post(
                url = path,
                headers = { "content-type": "application/json"}
            )

            if not domain_reply:
                print( domain_reply)
                raise SystemError("Could not reach casualdomain!")

            reply = domain_reply.json()

            domain['release'] = {
                "version": reply["result"]["version"]["casual"],
                "commit": reply["result"]["version"]["commit"]
            }

def scale_queue_forward(configuration, domain_name, alias, instances):
    for domain in configuration.get("domains",{}):
        if domain['lookup']['domain']['type'] == "casual":
            if domain['name'] == domain_name:
                reply = requests.post(
                    url = url_prefix( domain['lookup']) + "/.casual/queue/forward/scale/aliases",
                    json = { "aliases": [ { "name": alias, "instances": instances}]},
                    headers = { "content-type": "application/json"}
                )


def scale_instance(configuration, domain_name, alias, instances):
    for domain in configuration.get("domains",{}):
        if domain['lookup']['domain']['type'] == "casual":
            if domain['name'] == domain_name:
                reply = requests.post(
                    url = url_prefix( domain['lookup']) + "/.casual/domain/scale/instances",
                    json = { "aliases": [ { "name": alias, "instances": instances}]},
                    headers = { "content-type": "application/json"}
                )


def on_test_start( configuration: dict):
    setup_domains( configuration)
    start_domains( configuration)
    information( configuration)

    for domain in configuration.get("domains", {}):
        if domain['lookup']['domain']['type'] == "casual":

            # Warm up
            for i in range( 10):
                requests.post(
                    url = url_prefix( domain['lookup']) + "/casual/example/echo",
                    headers = { "content-type": "application/casual-x-octet"},
                    data = base64.b64encode( bytes( 1 * 1024))
                )

    # Reset casual metrics
    reset_metrics( configuration)


def on_test_stop( configuration, csv_prefix: str):
    metrics( configuration, csv_prefix)
    telegraf.metrics( configuration, csv_prefix)
    stop_domains( configuration)
    # remove_domains( configuration, environment)


def make_default_domain_env( domain: dict):

    casual_log = domain['lookup']['domain']['casual_log'] if "casual_log" in domain['lookup']['domain'] else "(error|warning|information)"
    casual_home = domain['lookup']['domain']['casual_home'] if "casual_home" in domain['lookup']['domain'] else "/opt/casual" 

    with open( f"{domain['home']}/domain.env", 'w') as file:
        file.write( f"""
export CASUAL_HOME={casual_home}
export PATH=$CASUAL_HOME/bin:$PATH 
export LD_LIBRARY_PATH=$CASUAL_HOME/lib:$LD_LIBRARY_PATH

# CASUAL_DOMAIN_HOME - this domain
export CASUAL_DOMAIN_HOME={domain['home']}

# Defines what will be logged.
export CASUAL_LOG='{(casual_log)}'

export CASUAL_LOG_PATH=$CASUAL_DOMAIN_HOME/logs/casual.log

""")


def make_base():
    location = tempfile.mkdtemp(dir="/var/tmp")
    print(f"BASEDIR for domains:[{location}]")
    return location


def make_home( home: str):
    os.makedirs( os.path.join( home, "configuration" ))
    os.makedirs( os.path.join( home, "logs" ))


def address( lookup: dict):
    return lookup['host']['user'] + "@" + lookup['host']['hostname']


def setup_domains( configuration: dict):
   
    for domain in configuration.get("domains", {}):
        make_home( domain['home'])

        default_domain_env = True

        for configuration_file in domain.get("files",[]):
            default_domain_env = False if configuration_file["filename"] == "domain.env" else default_domain_env
            filename = f"{domain['home']}/{configuration_file['filename']}"
            os.makedirs( os.path.dirname( filename), exist_ok=True)
            with open( filename, 'w') as file:
                file.write( configuration_file["content"])
                file.write( "\n")

        if default_domain_env:
            make_default_domain_env( domain)
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

        if helpers.is_remote(domain):
            helpers.execute(f'mkdir -p {domain["home"]}', address(domain['lookup']))
            helpers.copy_to_domain(f"{domain['home']}/*", '', domain, recursive=True)

    return configuration

def start_domains( configuration: dict):

    for domain in configuration.get("domains", {}):
        if not helpers.is_remote(domain):
            destination = "localhost"
        else:
            destination = address( domain['lookup'])

        helpers.execute(f'cd {domain["home"]} && . {domain["home"]}/domain.env && casual domain --boot configuration/domain.yaml', 
            destination)

    time.sleep(1.0)

def stop_domains( configuration: dict):

    for domain in configuration.get("domains", {}):
        if not helpers.is_remote(domain):
            destination = "localhost"
        else:
            destination = address( domain['lookup'])

        helpers.execute(f'cd {domain["home"]} && . {domain["home"]}/domain.env && casual domain --shutdown', destination)

    time.sleep(1.0)


def remove_domains( configuration: dict):

    for domain in configuration.get("domains", {}):
        if helpers.is_remote(domain):
            destination = address( domain['lookup'])
            helpers.execute(f'rm -rf {domain["home"]}', destination)

        helpers.execute(f'rm -rf {domain["home"]}')
