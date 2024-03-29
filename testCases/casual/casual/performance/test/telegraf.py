import os
from pathlib import Path
from locust.env import Environment
from casual.performance.test import helpers

def config( base: str, name: str, remote: dict):

    home = os.path.join( base, name)
    casual_home = remote["casual_home"] if "casual_home" in remote else "/opt/casual" 
    return {
            "name" : name,
            "home" : home,
            "remote": remote,
            "casual_statistics" : False,
            "files" : 
            [
               {
                  "filename" : "domain.env",
                  "content" : f"""
export CASUAL_HOME={casual_home}
export PATH=$CASUAL_HOME/bin:$PATH 
export LD_LIBRARY_PATH=$CASUAL_HOME/lib:$LD_LIBRARY_PATH

# CASUAL_DOMAIN_HOME - this domain
export CASUAL_DOMAIN_HOME={home}

# Defines what will be logged.
export CASUAL_LOG='(error|warning|information)'

export CASUAL_LOG_PATH=$CASUAL_DOMAIN_HOME/logs/casual.log

"""
               },
               {
                  "filename" : "configuration/domain.yaml",
                  "content" : f"""
domain:
  name: {name}

  executables:

    - alias: telegraf
      path: {remote['binpath']}/telegraf 
      arguments: [ -config, configuration/telegraf.conf]

"""
               },
               {
                  "filename" : "configuration/telegraf.conf",
                  "content" : """
###############################################################################
#                            INPUT PLUGINS                                    #
###############################################################################

# Telegraf configuration

[tags]
  tenant = "Casual"

# Configuration for telegraf agent
[agent]
  interval = "1s"
  round_interval = true
  flush_interval = "10s"
  flush_jitter = "0s"
  debug = false
  hostname = ""
  quiet = true

[[inputs.cpu]]
  percpu = false
  totalcpu = true
  drop = ["cpu_time"]

# Read metrics about memory usage
[[inputs.mem]]
  # no configuration


# Gather metrics about network interfaces
[[inputs.netstat]]

# Read metrics about swap memory usage
# This plugin ONLY supports Linux
[[inputs.swap]]
  # no configuration


[[outputs.file]]
  ## Files to write to, "stdout" is a specially handled file.
  files = ["logs/metrics.txt"]

  data_format = "json"
"""
               }
            ]
         }

def metrics( configuration: dict, environment: Environment):
   
   csv_prefix = environment.parsed_options.csv_prefix

   for domain in configuration.get("domains", {}):
      if 'remote' in domain and 'type' in domain['remote'] and domain['remote']['type'] == "telegraf":
        if not environment.parsed_options.use_remote_nodes:
          helpers.execute( f"cp {domain['home']}/logs/metrics.txt {csv_prefix}_{domain['name']}_telegraf.metrics.txt")

        else:
          source = domain['remote']['user'] + "@" + domain['remote']['host'] + ":" + domain['home']

          if source:
            helpers.scp( f"{source}/logs/metrics.txt", f"{csv_prefix}_{domain['name']}_telegraf.metrics.txt")

