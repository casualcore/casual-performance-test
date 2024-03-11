import os
from pathlib import Path
from locust.env import Environment

def config( base: str, name: str, remote: dict):

    home = os.path.join( base, name)
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
export CASUAL_HOME=$HOME/usr/local/casual
export PATH=$CASUAL_HOME/bin:$PATH 
export LD_LIBRARY_PATH=$CASUAL_HOME/lib:$LD_LIBRARY_PATH

# CASUAL_DOMAIN_HOME - this domain
export CASUAL_DOMAIN_HOME={home}

# Defines what will be logged.
export CASUAL_LOG='.*'

export TELEGRAF_HOME=/opt/homebrew/opt/telegraf
"""
               },
               {
                  "filename" : "configuration/domain.yaml",
                  "content" : f"""
domain:
  name: {name}

  executables:

    - alias: telegraf
      path: ${{TELEGRAF_HOME}}/bin/telegraf 
      arguments: [ -config, configuration/telegraf.conf, -config-directory, /opt/homebrew/etc/telegraf.d ]

"""
               },
               {
                  "filename" : "configuration/telegraf.conf",
                  "content" : """
###############################################################################
#                            INPUT PLUGINS                                    #
###############################################################################


[agent]
  quiet = true

# Read metrics about cpu usage
[[inputs.cpu]]
  ## Whether to report per-cpu stats or not
  percpu = true
  ## Whether to report total system cpu stats or not
  totalcpu = true
  ## If true, collect raw CPU time metrics
  collect_cpu_time = false
  ## If true, compute and report the sum of all non-idle CPU states
  ## NOTE: The resulting 'time_active' field INCLUDES 'iowait'!
  report_active = false
  ## If true and the info is available then add core_id and physical_id tags
  core_tags = false


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

  ## Data format to output.
  ## Each data format has its own unique set of configuration options, read
  ## more about them here:
  ## https://github.com/influxdata/telegraf/blob/master/docs/DATA_FORMATS_OUTPUT.md
  data_format = "json"

  ## The resolution to use for the metric timestamp.  Must be a duration string
  ## such as "1ns", "1us", "1ms", "10ms", "1s".  Durations are truncated to
  ## the power of 10 less than the specified units.
  json_timestamp_units = "1s"

"""
               }
            ]
         }

def metrics( configuration: dict, environment: Environment):
   
   csv_prefix = environment.parsed_options.csv_prefix

   for domain in configuration.get("domains", {}):
      if 'remote' in domain and 'type' in domain['remote'] and domain['remote']['type'] == "telegraf":
        if not environment.parsed_options.use_remote_nodes:
          os.system( f"cp {domain['home']}/logs/metrics.txt {csv_prefix}_{domain['name']}_metrics.txt")

        else:
          source = domain['remote']['user'] + "@" + domain['remote']['host']

          if source:
            os.system( f"scp {source}/logs/metrics.txt {csv_prefix}_{domain['name']}_metrics.txt")

