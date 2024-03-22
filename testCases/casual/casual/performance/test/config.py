import os
import yaml

model = {}

if not ( host_config_file:= os.getenv( "CASUAL_HOST_CONFIG_FILE")):
  raise SystemError( "CASUAL_HOST_CONFIG_FILE need to be set!")

if not os.path.exists( host_config_file):
  raise SystemError( f"{host_config_file} is missing!")

with open(host_config_file, 'r') as file:
  model['hosts'] = yaml.safe_load(file)['hosts']

if not ( domain_config_file:= os.getenv( "CASUAL_DOMAIN_CONFIG_FILE")):
  raise SystemError( "CASUAL_DOMAIN_CONFIG_FILE need to be set!")

if not os.path.exists( domain_config_file):
  raise SystemError( f"{domain_config_file} is missing!")

with open(domain_config_file, 'r') as file:
  model['domains'] = yaml.safe_load(file)['domains']

def domain( name):

  for entry in model['domains']:
    if entry['name'] == name:
      return entry

  raise SystemError(f"{name} is not found in {domain_config_file}")

def host( alias):
  if not ( site_name := os.getenv( "CASUAL_SITE_NAME")):
    raise SystemError( "CASUAL_SITE_NAME need to be set!")
    
  for entry in model['hosts'][site_name]:
    if entry['alias'] == alias:
      return entry

  raise SystemError(f"{alias} is not found in {host_config_file}")

def url_prefix(domain_name, host_alias):
  prefix = f"http://{host(host_alias)['hostname']}:{domain(domain_name)['inbound-http-port']}"
  return prefix

def port( name):
  return domain(name)['inbound-http-port']
