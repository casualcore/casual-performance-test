from locust import FastHttpUser, task, events
import base64
import requests
import os

global_host2 = "host2"
global_host3 = "host3"
global_uri = "http://{host}:8205".format(host=global_host2)
global_user2 = "cas205"
global_user3 = "cas-jca305"
global_service = "javaEcho"
global_10K = base64.b64encode( bytes( 10 * 1024))

class TestCase( FastHttpUser):
   """ Single service constant payload casual->jca """

   @task
   def task3( self):
      self.client.post("/casual/" + global_service,
         name = "10K",
         headers = { "content-type": "application/casual-x-octet"},
         data = global_10K)

@events.test_start.add_listener
def on_test_start( environment, **kwargs):
   print( "Test start")
   # Warm up
   for i in range( 10):
     requests.post(
         url = global_uri + "/casual/" + global_service,
         headers = { "content-type": "application/casual-x-octet"},
         data = global_10K)
   
   os.system("ssh {user}@{host} 'nohup telegraf -config telegraf.conf &>/dev/null &'".format(user=global_user2, host=global_host2))
   os.system("ssh {user}@{host} 'nohup telegraf -config telegraf.conf &>/dev/null &'".format(user=global_user3, host=global_host3))

@events.test_stop.add_listener
def on_test_stop( environment, **kwargs):
   os.system( "ssh {user}@{host} kill $(ssh {user}@{host} ps | grep telegraf | awk '{{print $1}}')".format(user=global_user2, host=global_host2))
   os.system( "scp {user}@{host}:metrics/telegraf.txt $HOME/testResults/005.constant.{user}.telegraf.metrics.txt".format(user=global_user2, host=global_host2))
   os.system( "ssh {user}@{host} kill $(ssh {user}@{host} ps | grep telegraf | awk '{{print $1}}')".format(user=global_user3, host=global_host3))
   os.system( "scp {user}@{host}:metrics/telegraf.txt $HOME/testResults/005.constant.{user}.telegraf.metrics.txt".format(user=global_user3, host=global_host3))
