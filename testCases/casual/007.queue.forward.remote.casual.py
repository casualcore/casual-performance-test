import os
from pathlib import Path
from casual.performance.test import casual
from casual.performance.test import configuration
from casual.performance.test import helpers
from casual.performance.test import lookup
from casual.performance.test import telegraf
import inspect
import time
import argparse


starttime = float()
stored_configuration = {}
testsuite = Path(__file__).stem


def domainX(base: str, host: str):
    """
    domain definition for a testdomain
    """

    # Use name of function as name of domain
    name = inspect.currentframe().f_code.co_name
    home = os.path.join(base, name)

    config_domain_X = configuration.Configuration( name, example_server=False)

    # gateway
    config_domain_X.domain.gateway.outbound.groups.append('outbound').connections.append( 
        lookup.inbound_gateway_address( "domainY", "hostB")
    )

    # queue
    config_domain_X.domain.queue.groups.append('test007').queues.append('test007.q1')
    config_domain_X.domain.queue.forward.groups.append('test007').services.append(source='test007.q1', target='casual/example/sleep')

    # executables
    config_domain_X.domain.executables.append(
        alias='prepare-queue',
        path='/bin/bash',
        arguments=[ '${CASUAL_DOMAIN_HOME}/configuration/enqueue_buffer.sh'])


    return {
            "name" : name,
            "home" : home,
            "lookup" : {
                "host": lookup.host( host),
                "domain" : lookup.domain( name)
            },
            "nginx_port" : lookup.port( name),
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


def domainY(base: str, host: str):
    """
    domain definition for a testdomain
    """

    # Use name of function as name of domain
    name = inspect.currentframe().f_code.co_name
    home = os.path.join(base, name)

    config_domain_Y = configuration.Configuration( name)
    config_domain_Y.domain.servers.find_first('casual-example-server').arguments = ['--sleep', '50ms', '--work', '20ms']
    # gateway
    config_domain_Y.domain.gateway.inbound.groups.append('inbound').connections.append( 
        lookup.inbound_gateway_address( "domainY", host)
    )

    return {
        "name" : name,
        "home" : home,
        "lookup" : {
            "host": lookup.host( "hostB"),
            "domain" : lookup.domain( name)
        },
        "files" : 
        [
            config_domain_Y.configuration_file_entry()
        ],
        "nginx_port" : lookup.port( name)
    }




def test_setup(csv_prefix: str):
    global starttime
    global stored_configuration

    base = casual.make_base()

    stored_configuration = {
        "domains":
        [
            telegraf.config( base, "telegrafA", lookup.domain( "telegrafA"), lookup.host( "hostA") ),
            telegraf.config( base, "telegrafB", lookup.domain( "telegrafB"), lookup.host( "hostB") ),
            domainX(base, "hostA"),
            domainY(base, "hostB")
        ]
    }

    casual.on_test_start(stored_configuration)
    starttime = helpers.write_start_information(stored_configuration, csv_prefix, testsuite)


def test_stop(csv_prefix):
    global starttime
    global stored_configuration

    casual.on_test_stop(stored_configuration, csv_prefix)
    helpers.write_stop_information(stored_configuration, csv_prefix, testsuite, starttime)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv', help="Prefix for csv files", required=True)
    parser.add_argument('-t', '--run-time', help="Total run time (in seconds)", type=float, default=60)
    arguments = parser.parse_args()

    print(f"test case file: {__file__}")

    test_setup(arguments.csv)

    # Run test here
    print("Test starting.")
    stage_time = float(arguments.run_time) / 8
    time.sleep(stage_time)

    casual.scale_instance(stored_configuration, "domainX", "prepare-queue", 0)
    casual.scale_queue_forward(stored_configuration, "domainX", "test007.q1", 1)
    casual.scale_instance(stored_configuration, "domainY", "casual-example-server", 1)
    time.sleep(stage_time)

    casual.scale_instance(stored_configuration, "domainX", "prepare-queue", 1)
    casual.scale_queue_forward(stored_configuration, "domainX", "test007.q1", 0)
    time.sleep(stage_time)

    casual.scale_instance(stored_configuration, "domainX", "prepare-queue", 0)
    casual.scale_queue_forward(stored_configuration, "domainX", "test007.q1", 2)
    casual.scale_instance(stored_configuration, "domainY", "casual-example-server", 2)
    time.sleep(stage_time)

    casual.scale_instance(stored_configuration, "domainX", "prepare-queue", 1)
    casual.scale_queue_forward(stored_configuration, "domainX", "test007.q1", 0)
    time.sleep(stage_time)

    casual.scale_instance(stored_configuration, "domainX", "prepare-queue", 0)
    casual.scale_queue_forward(stored_configuration, "domainX", "test007.q1", 4)
    casual.scale_instance(stored_configuration, "domainY", "casual-example-server", 4)
    time.sleep(stage_time)

    casual.scale_instance(stored_configuration, "domainX", "prepare-queue", 1)
    casual.scale_queue_forward(stored_configuration, "domainX", "test007.q1", 0)
    time.sleep(stage_time)

    casual.scale_instance(stored_configuration, "domainX", "prepare-queue", 0)
    casual.scale_queue_forward(stored_configuration, "domainX", "test007.q1", 8)
    casual.scale_instance(stored_configuration, "domainY", "casual-example-server", 8)
    time.sleep(stage_time)

    test_stop(arguments.csv)


if __name__ == '__main__':
    main()
