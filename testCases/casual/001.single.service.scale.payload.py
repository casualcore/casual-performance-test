from locust import FastHttpUser, task, events, constant
import base64
import requests
import os
from helpers import resetCasualMetrics, getCasualMetrics, writeStartInformation, writeStopInformation
import time
import csv

starttime=float()

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--use-remote-nodes", default=False, action='store_true', help="Remote node mode")

global_1B = base64.b64encode( bytes( 1))
global_1K = base64.b64encode( bytes( 1 * 1024))
global_10K = base64.b64encode( bytes( 10 * 1024))
global_100K = base64.b64encode( bytes( 100 * 1024))

class TestCase( FastHttpUser):
   """ Single service scale payload """
   wait_time = constant(1)


   @task
   def task1( self):
      self.client.post(
         name = "1B",
         url = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_1B)

   @task
   def task2( self):
      self.client.post(
         name = "1K",
         url = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_1K)

   @task
   def task3( self):
      self.client.post(
         name = "10K",
         url = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_10K)

   @task
   def task4( self):
      self.client.post(
         name = "100K",
         url = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_100K)

@events.test_start.add_listener
def on_test_start( environment, **kwargs):
   global starttime
   # Warm up
   for i in range( 10):
      requests.post(
         url = environment.host + "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_1K)

   # Start telegraf
   if environment.parsed_options.use_remote_nodes:
      os.system( "ssh cas201@host2 'nohup telegraf -config telegraf.conf &>/dev/null &'")

   starttime = writeStartInformation( environment)

   # Reset casual metrics
   resetCasualMetrics( environment.host)

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
   global starttime

   # Stop telegraf
   if environment.parsed_options.use_remote_nodes:
      os.system( "ssh cas201@host2 kill $(ssh cas201@host2 ps | grep telegraf | awk '{print $1}')")
      os.system( "scp cas201@host2:metrics/telegraf.txt $HOME/testResults/001.cas201.telegraf.metrics.txt")

   # Get casual metrics
   getCasualMetrics( environment.host, "001", "cas201")

   writeStopInformation( environment, starttime)
