import os
from casual.performance.test import casual, helpers, lookup

def config( base: str, name: str, host_alias: str):

    home = os.path.join( base, name)
    domain = lookup.domain(name)
    casual_home = domain["casual_home"] if "casual_home" in domain else "/opt/casual" 
    return {
            "name" : name,
            "home" : home,
            "lookup" : {
                "host": lookup.host(host_alias),
                "domain" : domain
            },
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
      path: {domain['binpath']}/telegraf 
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


def metrics( domain: dict, csv_prefix: str):
    helpers.copy_from_domain('logs/metrics.txt', f"{csv_prefix}_{domain['name']}_telegraf.metrics.txt", domain)


def information( domain: dict):
    pass


def warmup( domain: dict):
    pass


def reset_metrics( domain: dict):
    pass


def setup_domain( domain: dict):
    casual.setup_domain( domain)


def start_domain( domain: dict):
    casual.start_domain( domain)


def stop_domain( domain: dict):
    casual.stop_domain( domain)
