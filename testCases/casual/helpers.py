import requests
import os

def resetCasualMetrics( host):
   requests.post(
      url = host + "/casual/.casual/service/metric/reset",
      headers = { "content-type": "application/json"}
   )


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
