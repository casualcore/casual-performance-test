import csv
import importlib
import os
import subprocess
import tempfile
import time

beginning = 0
end = 1

domain_type_modules = {
    'casual': importlib.import_module('casual.performance.test.casual'),
    'telegraf': importlib.import_module('casual.performance.test.telegraf'),
    'jca': importlib.import_module('casual.performance.test.jca')
}


def has_name(name: str):
    return lambda x: x['name'] == name


def get_domain(configuration: dict, name: str):
    return next( filter( has_name(name), configuration.get("domains", {})), None)


def call_function(fn_name: str, domain: dict, **kwargs):
    domain_type = domain['lookup']['domain']['type']
    module = domain_type_modules[domain_type]
    fn = getattr(module, fn_name)
    return fn(domain, **kwargs)


def is_remote( domain: dict):
    return domain['lookup']['host']['hostname'] != 'localhost'


def make_base():
    location = tempfile.mkdtemp(dir="/var/tmp")
    print(f"BASEDIR for domains:[{location}]")
    return location


def metrics(configuration: dict, csv_prefix: str):
    for domain in configuration.get("domains", {}):
        call_function('metrics', domain, csv_prefix=csv_prefix)


def information(configuration: dict):
    for domain in configuration.get("domains", {}):
        call_function('information', domain)


def setup_domains(configuration: dict):
    for domain in configuration.get("domains", {}):
        call_function('setup_domain', domain)
    

def start_domains(configuration: dict):
    for domain in configuration.get("domains", {}):
        call_function('start_domain', domain)


def warmup(configuration: dict):
    for domain in configuration.get("domains", {}):
        call_function('warmup', domain)


def stop_domains(configuration: dict):
    for domain in configuration.get("domains", {}):
        call_function('stop_domain', domain)


def reset_metrics(configuration: dict):
    for domain in configuration.get("domains", {}):
        call_function('reset_metrics', domain)


def on_test_start(configuration: dict):
    setup_domains( configuration)
    start_domains( configuration)
    information( configuration)
    warmup( configuration)
    reset_metrics( configuration)


def on_test_stop(configuration: dict, csv_prefix: str):
    metrics( configuration, csv_prefix)
    stop_domains( configuration)
    # remove_domains( configuration)


def write_start_information( csv_prefix: str, testsuite:str):
    version = "test"
    commit = "test"
    now = time.time()

    with open( f"{csv_prefix}_testrun.csv", 'w', newline='') as csvfile:
        fieldnames = ['Id', 'Timestamp', 'Type', 'Version', 'Commit', 'TestSuite']

        writer = csv.DictWriter( csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerow( { 'Id' : now, 'Timestamp' : now, 'Type': beginning, 'Version' : version, 'Commit' : commit, 'TestSuite' : testsuite } )

    return now


def write_stop_information( csv_prefix: str, testsuite: str, starttime):
    version = "" 
    commit = "" 
    now = time.time()

    with open( f"{csv_prefix}_testrun.csv", 'a', newline='') as csvfile:
        fieldnames = [ 'Id', 'Time', 'Type','Version', 'Commit', 'TestSuite']

        writer = csv.DictWriter( csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writerow( { 'Id': starttime, 'Time' : now, 'Type': end, 'Version' : version, 'Commit' : commit, 'TestSuite' : testsuite } )


def execute( command: str, host: str = "localhost" ):
    if host == "localhost":
        print(f'execute command: {command}')
        subprocess.Popen( command, shell=True)
    else:
        remote_command = f"ssh {host} '{command} > logs/console.log 2>&1 '"
        print(f'execute remote command: {remote_command}')
        subprocess.Popen( remote_command, shell=True)
    time.sleep(1.0)


def scp( source: str, destination: str, recursive = False):
    command = "scp -r" if recursive else "scp" 
    print( f'scp: {command} {source} {destination}')
    os.system( f"{command} {source} {destination}")
    time.sleep( 1.0)


def copy_from_domain( source: str, destination: str, domain: dict, recursive = False):
    if is_remote( domain):
        user = domain['lookup']['host']['user']
        hostname = domain['lookup']['host']['hostname']
        scp( f"{user}@{hostname}:{domain['home']}/{source}", destination, recursive=recursive)
    else:
        execute( f'cp {domain["home"]}/{source} {destination}')


def copy_to_domain( source: str, destination: str, domain: dict, recursive = False):
    if is_remote( domain):
        user = domain['lookup']['host']['user']
        hostname = domain['lookup']['host']['hostname']
        scp( source, f"{user}@{hostname}:{domain['home']}/{destination}", recursive=recursive)
    else:
        execute( f"cp {source} {domain['home']}/{destination}")
