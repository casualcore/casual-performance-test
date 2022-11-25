from locust import FastHttpUser, task, events
import base64
import requests
import os
from helpers import *

global_host = "http://host2:8203"
global_host2 = "http://host3:8303"
global_1B = base64.b64encode( bytes( 1))
global_1K = base64.b64encode( bytes( 1 * 1024))
global_10K = base64.b64encode( bytes( 10 * 1024))
global_100K = base64.b64encode( bytes( 100 * 1024))

class TestCase( FastHttpUser):
   """ Single service scale payload multiple domains """

   @task
   def task1( self):
      self.client.post(
         name = "1B",
         path = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_1B)

   @task
   def task2( self):
      self.client.post(
         name = "1K",
         path = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_1K)

   @task
   def task3( self):
      self.client.post(
         name = "10K",
         path = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_10K)

   @task
   def task4( self):
      self.client.post(
         name = "100K",
         path = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_100K)


@events.test_start.add_listener
def on_test_start( environment, **kwargs):
   # Warm up
   for i in range( 10):
      requests.post(
         url = global_host + "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_1K)
   
   # Start telegraf
   os.system( "ssh cas201@host2 'nohup telegraf -config telegraf.conf &>/dev/null &'")
   os.system( "ssh cas301@host3 'nohup telegraf -config telegraf.conf &>/dev/null &'")

   # Reset casual metrics
   resetCasualMetrics( global_host)
   resetCasualMetrics( global_host2)

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
   # Stop telegraf
   os.system( "ssh cas201@host2 kill $(ssh cas201@host2 ps | grep telegraf | awk '{print $1}')")
   os.system( "scp cas201@host2:metrics/telegraf.txt $HOME/testResults/003.cas201.telegraf.metrics.txt")
   os.system( "ssh cas301@host3 kill $(ssh cas301@host3 ps | grep telegraf | awk '{print $1}')")
   os.system( "scp cas301@host3:metrics/telegraf.txt $HOME/testResults/003.cas301.telegraf.metrics.txt")

   # Get casual metrics
   getCasualMetrics( global_host, "003", "cas203")
   getCasualMetrics( global_host, "003", "cas303")
      
