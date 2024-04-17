import argparse
import inspect
import os
import time
from pathlib import Path

from casual.performance.test import (casual, configuration, helpers, lookup,
                                     telegraf)

starttime = float()
stored_configuration = {}
testsuite = Path(__file__).stem


def domainX(base: str, host_alias: str):
    """
    domain definition for a testdomain
    """

    # Use name of function as name of domain
    name = inspect.currentframe().f_code.co_name
    home = os.path.join(base, name)

    config_domain_X = configuration.Configuration( name)

    # queue
    config_domain_X.domain.queue.groups.append('test007').queues.append('test007.q1')
    config_domain_X.domain.queue.forward.groups.append('test007').services.append(source='test007.q1', target='casual/example/sleep')

    # executables
    config_domain_X.domain.executables.append(
        alias='prepare-queue',
        path='/bin/bash',
        arguments=[ '${CASUAL_DOMAIN_HOME}/configuration/enqueue_buffer.sh'])

    config_domain_X.domain.servers.find_first('casual-example-server').arguments = ['--sleep', '50ms', '--work', '20ms']

    return {
            "name" : name,
            "home" : home,
            "lookup" : {
                "host": lookup.host( host_alias),
                "domain" : lookup.domain( name)
            },
            "nginx_port" : lookup.inbound_http_port( name),
            "files" : 
            [
                config_domain_X.configuration_file_entry(),
                {
                    "filename" : "configuration/enqueue_buffer.sh",
                    "content" : f"""
num_messages=64
message_size=1024
for x in $(seq 1 $num_messages)
do
   head -c $message_size /dev/urandom | casual buffer --compose '.binary/' | casual queue --enqueue test007.q1
done
"""
                },
            ]
    }


def test_setup(csv_prefix: str):
    global starttime
    global stored_configuration

    base = helpers.make_base()

    stored_configuration = {
        "domains":
        [
            telegraf.config( base, "telegrafA", "hostA"),
            domainX(base, "hostA")
        ]
    }

    helpers.on_test_start( stored_configuration)
    starttime = helpers.write_start_information( csv_prefix, testsuite)


def test_stop(csv_prefix):
    global starttime
    global stored_configuration

    helpers.on_test_stop( stored_configuration, csv_prefix)
    helpers.write_stop_information( csv_prefix, testsuite, starttime)


def test_stage(instances: int, stage_time: float):
    dX = helpers.get_domain(stored_configuration, "domainX")
    
    # Fill queue
    casual.scale_queue_forward(dX, "test007.q1", 0)
    casual.scale_instance(dX, "casual-example-server", 0)
    casual.scale_instance(dX, "prepare-queue", 1)
    time.sleep(stage_time / 2.0)

    # Process queue
    casual.scale_instance(dX, "prepare-queue", 0)
    casual.scale_instance(dX, "casual-example-server", instances)
    casual.scale_queue_forward(dX, "test007.q1", instances)
    time.sleep(stage_time / 2.0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv', help="Prefix for csv files", required=True)
    parser.add_argument('-t', '--run-time', help="Total run time (in seconds)", type=float, default=60)
    arguments = parser.parse_args()

    test_setup(arguments.csv)

    # Run test here
    print("Test starting.")
    stage_time = float(arguments.run_time) / 4
    
    test_stage(1, stage_time)
    test_stage(2, stage_time)
    test_stage(4, stage_time)
    test_stage(8, stage_time)

    test_stop(arguments.csv)


if __name__ == '__main__':
    main()
