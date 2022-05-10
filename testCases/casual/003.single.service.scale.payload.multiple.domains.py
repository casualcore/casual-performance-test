from locust import FastHttpUser, task, events
import base64
import requests

global_host = "http://host2:8203"
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
   print( "Test start")
   # Warm up
   for i in range( 10):
     requests.post(
         url = global_host + "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_1K)
   
   #TODO reset casual metrics

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
   print( "Test done")
   #TODO get casual metrics
      
