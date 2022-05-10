from locust import FastHttpUser, task, LoadTestShape, events
import base64
import requests

global_host = "http://host2:8204"
global_10K = base64.b64encode( bytes( 10 * 1024))

class TestCase( FastHttpUser):
   """ Scale services constant payload multiple domains """

   host =  global_host

   @task
   def task1( self):
      self.client.post(
         name = "10K",
         path = "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_10K)


@events.test_start.add_listener
def on_test_start( environment, **kwargs):
   print( "Test start")
   # Warm up
   for i in range( 10):
     requests.post(
         url = global_host + "/casual/casual/example/echo",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_10K)
   
   #TODO reset casual metrics

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
   print( "Test done")
   #TODO get casual metrics
      
class LoadShape( LoadTestShape):
   time_limit = 10 # seconds
   user_count = 10
   spawn_rate = 1

   def tick( self):
      run_time = self.get_run_time()

      if run_time < self.time_limit:
         return ( self.user_count, self.spawn_rate)

      return None