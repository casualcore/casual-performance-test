import requests
import os
import json
import sys
import time
from pathlib import Path
import csv

beginning = 0
end = 1

def resetCasualMetrics( host):
   requests.post(
      url = host + "/casual/.casual/service/metric/reset",
      headers = { "content-type": "application/json"}
   )

def getCasualInformation( host):
   domain_reply = requests.post(
      url = host + "/casual/.casual/domain/state",
      headers = { "content-type": "application/json"}
   )

   if not domain_reply:
      raise SystemError("Could not reach casualdomain!")

   reply = domain_reply.json()

   return reply["result"]["version"]["casual"], reply["result"]["version"]["commit"]

def writeStartInformation( environment):
   version, commit = getCasualInformation( environment.host)

   now = time.time()

   csv_prefix = environment.parsed_options.csv_prefix
   testsuite = Path( environment.parsed_options.locustfile).stem

   with open(f"{csv_prefix}_testrun.csv", 'w', newline='') as csvfile:
      fieldnames = ['Id', 'Timestamp', 'Type', 'Version', 'Commit', 'TestSuite']

      writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
      writer.writeheader()
      writer.writerow( { 'Id' : now, 'Timestamp' : now, 'Type': beginning, 'Version' : version, 'Commit' : commit, 'TestSuite' : testsuite } )

   return now

def writeStopInformation( environment, starttime):
   version = "" 
   commit = "" 

   now = time.time()

   csv_prefix = environment.parsed_options.csv_prefix
   testsuite = Path( environment.parsed_options.locustfile).stem

   with open(f"{csv_prefix}_testrun.csv", 'a', newline='') as csvfile:
      fieldnames = [ 'Id', 'Time', 'Type','Version', 'Commit', 'TestSuite']

      writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
      writer.writerow( { 'Id': starttime, 'Time' : now, 'Type': end, 'Version' : version, 'Commit' : commit, 'TestSuite' : testsuite } )


def getCasualMetrics( host, testCase, domain):
   domain_reply = requests.post(
      url = host + "/casual/.casual/domain/state",
      headers = { "content-type": "application/json"}
   )
   service_reply = requests.post(
      url = host + "/casual/.casual/service/state",
      headers = { "content-type": "application/json"}
   )
   transaction_reply = requests.post(
      url = host + "/casual/.casual/transaction/state",
      headers = { "content-type": "application/json"}
   )

   user_home = os.environ[ 'HOME']

   # Domain metrics
   f = open( user_home + "/testResults/" + testCase + "." + domain + ".domain.metrics.json", "w")
   f.write( domain_reply.text)
   f.close()

   # Service metrics
   f = open( user_home + "/testResults/" + testCase + "." + domain + ".service.metrics.json", "w")
   f.write( service_reply.text)
   f.close()

   # Transaction metrics
   f = open( user_home + "/testResults/" + testCase + "." + domain + ".transaction.metrics.json", "w")
   f.write( transaction_reply.text)
   f.close()
