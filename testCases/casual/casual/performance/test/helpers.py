import os
import time
import csv
import subprocess

beginning = 0
end = 1

def is_remote( domain: dict):
    return domain['lookup']['host']['hostname'] != 'localhost'


def write_start_information( configuration: dict, csv_prefix: str, testsuite:str):
    version = "test"
    commit = "test"
    now = time.time()

    with open( f"{csv_prefix}_testrun.csv", 'w', newline='') as csvfile:
        fieldnames = ['Id', 'Timestamp', 'Type', 'Version', 'Commit', 'TestSuite']

        writer = csv.DictWriter( csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerow( { 'Id' : now, 'Timestamp' : now, 'Type': beginning, 'Version' : version, 'Commit' : commit, 'TestSuite' : testsuite } )

    return now


def write_stop_information( configuration: dict, csv_prefix: str, testsuite: str, starttime):
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
