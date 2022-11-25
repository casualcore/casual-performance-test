from locust import FastHttpUser, task, events
import base64
import requests
import os
from helpers import *

global_host = "http://host2:8204"
global_host2 = "http://host3:8304"
global_10K = base64.b64encode( bytes( 10 * 1024))

class TestCase( FastHttpUser):
   """ Scale services constant payload multiple domains """

   @task
   def task1( self):
      self.client.post(
         name = "10K",
         path = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_10K)


@events.test_start.add_listener
def on_test_start( environment, **kwargs):
   # Warm up
   for i in range( 10):
      requests.post(
         url = global_host + "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_10K)
   
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
   os.system( "scp cas201@host2:metrics/telegraf.txt $HOME/testResults/004.cas201.telegraf.metrics.txt")
   os.system( "ssh cas301@host3 kill $(ssh cas301@host3 ps | grep telegraf | awk '{print $1}')")
   os.system( "scp cas301@host3:metrics/telegraf.txt $HOME/testResults/004.cas301.telegraf.metrics.txt")

   # Get casual metrics
   getCasualMetrics( global_host, "004", "cas204")
   getCasualMetrics( global_host, "004", "cas304")
      