import requests
import os
import json
import sys
import time
from pathlib import Path
import csv
import tempfile
from locust.env import Environment
import subprocess

beginning = 0
end = 1

def write_start_information( configuration: dict, environment: Environment):

   now = time.time()

   version = "test"
   commit = "test"
   csv_prefix = environment.parsed_options.csv_prefix
   testsuite = Path( environment.parsed_options.locustfile).stem

   with open(f"{csv_prefix}_testrun.csv", 'w', newline='') as csvfile:
      fieldnames = ['Id', 'Timestamp', 'Type', 'Version', 'Commit', 'TestSuite']

      writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
      writer.writeheader()
      writer.writerow( { 'Id' : now, 'Timestamp' : now, 'Type': beginning, 'Version' : version, 'Commit' : commit, 'TestSuite' : testsuite } )

   return now

def write_stop_information( configuration: dict, environment: Environment, starttime):
   version = "" 
   commit = "" 

   now = time.time()

   csv_prefix = environment.parsed_options.csv_prefix
   testsuite = Path( environment.parsed_options.locustfile).stem

   with open(f"{csv_prefix}_testrun.csv", 'a', newline='') as csvfile:
      fieldnames = [ 'Id', 'Time', 'Type','Version', 'Commit', 'TestSuite']

      writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
      writer.writerow( { 'Id': starttime, 'Time' : now, 'Type': end, 'Version' : version, 'Commit' : commit, 'TestSuite' : testsuite } )

def retrieve_host( domain: str, user_config: list):

   for entry in user_config.get("config", []):
      if domain == entry["domain"]:
         return entry["host"]
      
   raise SystemError( f"No user-config for domain {domain}")


def execute( command: str, host: str = "localhost" ):

   if host == "localhost":
      subprocess.Popen( command, shell=True)
   else:
      remote_command = f"ssh {host} '{command} > logs/console.log 2>&1 '"
      subprocess.Popen( remote_command, shell=True)

def scp( source: str, destination: str, recursive = False):

   command = "scp -r" if recursive else "scp" 

   os.system(f"{command} {source} {destination}")



